from flask import Flask, Response, request
from sqlalchemy import Engine
from pydantic import ValidationError

from app.services.info_service import generate_summary
from app.schemas.query_params import InfoQueryParams

import logging

logger: logging.Logger = logging.getLogger(__name__)

def register_routes(app: Flask, engine: Engine):
    """
    Регистрирует все маршруты приложения.
    """
    @app.route("/info")
    def get_info():
        """
        Эндпоинт для получения сводки о сервисе с поддержкой query параметров.
        """
        try:
            params = InfoQueryParams(name=request.args.get("name"))
        except ValidationError as e:
            logger.warning(f"Неверные параметры запроса: {e}")
            return Response(
                f"Ошибка в параметрах запроса:\n{e}", status=400, mimetype="text/plain"
            )

        return generate_summary(engine, params)
