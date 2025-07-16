from flask import Flask
from sqlalchemy import create_engine, Engine
from app.config import Config
from app.database.models import Base
from app.services.api_fetcher import fetch_and_update_db
from app.services.logger import setup_logger
from app.controllers.info_controller import register_routes
import threading
import logging

setup_logger()
logger: logging.Logger = logging.getLogger(__name__)

app: Flask = Flask(__name__)

engine: Engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(bind=engine)

register_routes(app, engine)

threading.Thread(target=fetch_and_update_db, args=(engine,), daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, threaded=True)
