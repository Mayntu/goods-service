from flask import Response, request
from sqlalchemy import Engine, func
from sqlalchemy.orm import Session

from app.database.models import Product, Category
from app.schemas.query_params import InfoQueryParams

import logging

logger: logging.Logger = logging.getLogger(__name__)


def generate_summary(engine: Engine, params: InfoQueryParams) -> Response:
    """
    Формирует текстовую сводку о состоянии БД с учётом фильтрации.
    """
    session: Session = Session(bind=engine)
    try:
        query = session.query(Product)

        # Применяем фильтрацию по имени, если задано
        if params.name:
            query = query.filter(Product.name.ilike(f"%{params.name}%"))

        total_products: int = query.count()
        total_categories: int = session.query(func.count(Category.id)).scalar()
        average_price: float = session.query(func.avg(Product.price)).scalar() or 0

        products = query.order_by(Product.id).limit(10).all()

        summary_lines = [
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║                        📦 Сводка о базе данных                        ║",
            "╠══════════════════════════════════════════════════════════════════════╣",
            f"║ ✅ Всего товаров (по фильтру): {total_products:<32}║",
            f"║ ✅ Всего категорий            : {total_categories:<32}║",
            f"║ 💵 Средняя цена               : {average_price:<32.2f}₽║",
            "╠══════════════════════════════════════════════════════════════════════╣",
            "║ 🔥 Примеры товаров (до 10 шт):                                        ║",
            "╠═════╦════════════════════════════════════╦══════════╦════════════════╣",
            "║ ID  ║ Название                           ║   Цена   ║ Категория      ║",
            "╠═════╬════════════════════════════════════╬══════════╬════════════════╣",
        ]

        if products:
            for p in products:
                summary_lines.append(
                    f"║ {p.product_id:<3} ║ {p.name[:34]:<34} ║ {p.price:<8.2f}₽ ║ {p.category.name[:14]:<14} ║"
                )
        else:
            summary_lines.append(
                "║                  ⚠️ Нет товаров по фильтру.                        ║"
            )

        summary_lines.append(
            "╚═════╩════════════════════════════════════╩══════════╩════════════════╝"
        )

        logger.info("Сводка отправлена клиенту")
        return Response("\n".join(summary_lines), mimetype="text/plain")

    finally:
        session.close()
