import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=1000000, backupCount=3),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)