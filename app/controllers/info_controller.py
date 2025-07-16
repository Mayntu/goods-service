from flask import Flask, Response
from sqlalchemy import Engine
from app.services.info_service import generate_summary


def register_routes(app: Flask, engine: Engine):
    """
    Регистрирует все маршруты приложения.
    """
    @app.route("/info")
    def get_info():
        """
        Эндпоинт для получения сводки о сервисе.
        """
        return generate_summary(engine)
