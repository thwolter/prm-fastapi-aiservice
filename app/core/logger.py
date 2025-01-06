import logging
import sys

from core.config import settings

LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s [%(name)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)