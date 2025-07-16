from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.database.models import Base, Product, Category
from app.config import Config
from app.services.logger import setup_logger

import time
import requests
import logging

setup_logger()
logger: logging.Logger = logging.getLogger(__name__)

API_URLS: list[str] = [
    "https://bot-igor.ru/api/products?on_main=true",
    "https://bot-igor.ru/api/products?on_main=false"
]


def fetch_and_update_db(engine: Engine):
    """
    Функция для периодического получения данных из API и обновления базы данных.
    Запускается в отдельном потоке.
    :param engine: SQLAlchemy Engine для подключения к базе данных.
    :return: None
    """
    while True:
        logger.info("Начало обновления БД с данных API")
        session: Session = Session(bind=engine)
        try:
            for url in API_URLS:
                logger.info(f"Получение данных с {url}")
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                if isinstance(data, dict):
                    if 'products' in data:
                        products = data['products']
                    else:
                        logger.warning(f"Нет ключа products в апи {url}")
                        continue
                else:
                    logger.error(f"Неожиданный формат ответа от апи {data}")
                    continue

                for item in products:
                    try:
                        product_api_id: int = item.get('Product_ID')
                        if not product_api_id:
                            logger.warning(f"Пропущен продукт без Product_ID: {item}")
                            continue

                        product_name: str = item.get('Product_Name', 'Unknown')

                        category_data = item.get('categories', [])
                        if category_data:
                            category_name: str = category_data[0].get('Category_Name', 'Uncategorized')
                        else:
                            category_name = 'Uncategorized'

                        category: Category = session.query(Category).filter_by(name=category_name).first()
                        if not category:
                            category = Category(name=category_name)
                            session.add(category)
                            session.commit()
                            logger.info(f"Добавлена новая категория: {category_name}")

                        parameters = item.get('parameters', [])
                        price = None
                        if parameters:
                            price = parameters[0].get('price')
                        if price is None:
                            logger.warning(f"Не найдена цена для продукта: {product_name}")
                            continue

                        images = item.get('images', [])
                        image_url = ''
                        for img in images:
                            if img.get('MainImage'):
                                image_url = img.get('Image_URL', '')
                                break

                        product: Product = session.query(Product).filter_by(product_id=product_api_id).first()
                        if product:
                            updated = False

                            if product.name != product_name:
                                product.name = product_name
                                updated = True
                            if product.price != price:
                                product.price = price
                                updated = True
                            if product.image_url != image_url:
                                product.image_url = image_url
                                updated = True
                            if product.category != category:
                                product.category = category
                                updated = True

                            if updated:
                                logger.info(f"Обновлен продукт: {product_name} (ID: {product_api_id})")
                            else:
                                logger.info(f"Продукт без изменений: {product_name} (ID: {product_api_id})")
                        else:
                            product = Product(
                                product_id=product_api_id,
                                name=product_name,
                                price=price,
                                image_url=image_url,
                                category=category
                            )
                            session.add(product)
                            logger.info(f"Добавлен новый продукт: {product_name} (ID: {product_api_id})")

                    except Exception as product_error:
                        logger.error(f"Ошибка обработки продукта {item}: {product_error}")
                        continue

                session.commit()
                logger.info(f"Данные с {url} успешно сохранены в БДшку")

        except Exception as e:
            logger.error(f"Глобальная ошибка при обработке апи {e}")
            session.rollback()
        finally:
            session.close()

        logger.info(f"Завершено обновление. Следующее через {Config.API_UPDATE_INTERVAL} секунд")
        time.sleep(Config.API_UPDATE_INTERVAL)