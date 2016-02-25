"""
Backend factory
"""

# TODO: Implement real factory

import logging
import os

from isk import __version__
from isk.conf import settings
from isk.backends.imgseeklib.imagedb import ImgDB


logger = logging.getLogger(__name__)

db_path = os.path.expanduser(settings.DATABASE_PATH)

logger.info("+- Initializing isk api (version %s) ...", __version__)

backend = ImgDB(settings.AUTOMATIC_SAVE, settings.SAVE_INTERVAL)
backend.loadalldbs(db_path)

logger.info("| image database initialized")
logger.info("| using database from %s", db_path)
