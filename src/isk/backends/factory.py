"""
Backend factory
"""

# TODO: Implement real factory

import logging
import os

from isk import settings, __version__
from isk.backends.imgseeklib.imagedb import ImgDB


logger = logging.getLogger(__name__)

db_path = os.path.expanduser(settings.core.get('database', 'databasePath'))

logger.info("+- Initializing isk api (version %s) ...", __version__)

backend = ImgDB(settings)
backend.loadalldbs(db_path)

logger.info("| image database initialized")
logger.info("| using database from %s", db_path)