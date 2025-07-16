from flask import Response
from sqlalchemy import Engine, func
from sqlalchemy.orm import Session
from app.database.models import Product, Category
import logging

logger: logging.Logger = logging.getLogger(__name__)


def generate_summary(engine: Engine) -> Response:
    """
    Формирует текстовую сводку о состоянии БД.
    """
    session: Session = Session(bind=engine)
    try:
        total_products: int = session.query(func.count(Product.id)).scalar()
        total_categories: int = session.query(func.count(Category.id)).scalar()
        average_price: float = session.query(func.avg(Product.price)).scalar() or 0

        first_product: Product = session.query(Product).order_by(Product.id).first()

        summary = [
            "===== 📦 Сводка о базе данных =====",
            f"✅ Всего товаров: {total_products}",
            f"✅ Всего категорий: {total_categories}",
            f"💵 Средняя цена: {average_price:.2f}₽",
        ]

        if first_product:
            summary += [
                "🔥 Пример товара:",
                f"   - Название: {first_product.name}",
                f"   - Цена: {first_product.price}₽",
                f"   - Категория: {first_product.category.name}",
                f"   - Фото: {first_product.image_url}",
            ]

        summary.append("===================================")
        logger.info("Сводка отправлена клиенту")

        return Response("\n".join(summary), mimetype="text/plain")
    finally:
        session.close()
