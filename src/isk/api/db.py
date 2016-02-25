"""
Image database management API
"""

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


def save_db(db_id: int) -> bool:
    """
    Save the supplied database space if the it has already been saved with a filename (previous call to L{saveDbAs}).
    B{NOTE}: This operation should be used for exporting single database spaces.
    For regular server instance database persistance, use L{saveAllDbs} and L{loadAllDbs}.

    :since: 0.7
    :param db_id: Database space id.
    :return:  True in case of success.
    """
    return backend.savedb(db_id)


def save_db_as(db_id: int, filename: str) -> bool:
    """
    Save the supplied database space if the it has already been saved with a filename
    (subsequent save calls can be made to L{saveDb}).

    :since: 0.7
    :param db_id: Database space id.
    :param filename: Target filesystem full path of the file where data should be stored at.
        B{NOTE}: This data file contains a single database space and should be used for import/export purposes only.
        Do not try to load it with a call to L{loadAllDbs}.
    :return:  1 in case of success.
    """
    return backend.savedbas(db_id, filename)


def load_db(db_id: int, filename: str) -> int:
    """
    Load the supplied single-database-space-dump into a database space of given id.
    An existing database space with the given id will be completely replaced.

    :since: 0.7
    :param db_id: Database space id.
    :param filename: Target filesystem full path of the file where data is stored at.
        B{NOTE}: This data file contains a single database space and should be used for import/export purposes only.
        Do not try to load it with a call to L{loadAllDbs} and vice versa.
    :return:  dbId in case of success.
    """
    return backend.loaddb(db_id, filename)


def reset_db(db_id: int) -> bool:
    """
    Removes all images from a database space, frees memory, reset statistics.

    :since: 0.7
    :param db_id: Database space id.
    :return:  True in case of success.
    """
    return backend.resetdb(db_id)


def create_db(db_id: int) -> int:
    """
    Create new db space. Overwrite database space statistics if one with supplied id already exists.

    :since: 0.7
    :param db_id: Database space id.
    :return:  dbId in case of success
    """
    created_id = backend.createdb(db_id)
    return created_id


def get_db_img_count(db_id) -> int:
    """
    Return count of indexed images on database space.

    :since: 0.7
    :param db_id: Database space id.
    :return:  image count
    """
    db_id = int(db_id)
    return backend.get_img_count(db_id)


def get_db_list() -> tuple:
    """
    Return list defined database spaces.

    :since: 0.7
    :return:  array of db space ids
    """
    return backend.get_db_list()


def get_db_detailed_list() -> dict:
    """
    Return details for all database spaces.

    :return:  Dict with detailed info about each db space
    """

    return backend.get_db_detailed_list()


def save_all_dbs_as(path: str) -> int:
    """
    Persist all existing database spaces.

    :since: 0.7
    :param path: Target filesystem full path of the file where data is stored at.
    :return:  total db spaces written
    """

    return backend.savealldbs(path)


def save_all_dbs() -> int:
    """
    Persist all existing database spaces on the data file defined at the config file I{settings.py}

    :since: 0.7
    :return:  count of persisted db spaces
    """

    return backend.savealldbs(db_path)


def load_all_dbs_as(path: str) -> int:
    """
    Loads from disk all previously persisted database spaces. (File resulting from a previous call to L{saveAllDbs}).

    :since: 0.7
    :param path: Target filesystem full path of the file where data is stored at.
    :return:  total db spaces read
    """

    return backend.loadalldbs(path)


def load_all_dbs() -> int:
    """
    Loads from disk all previously persisted database spaces on the data file defined at the config file I{settings.py}

    :since: 0.7
    :return:  count of persisted db spaces
    """

    return backend.loadalldbs(db_path)


def remove_db(db_id: int) -> bool:
    """
    Remove a database. All images associated with it are also removed.

    :since: 0.7
    :param db_id: Database ID.
    :return:  True if succesful
    """

    return backend.remove_db(db_id)


def is_valid_db(db_id: int) -> bool:
    """
    Return whether database space id has already been defined

    :since: 0.7
    :param db_id: Database space id.
    :return:  True if exists
    """

    return backend.is_valid_db(db_id)


exporting = (
    save_db,
    load_db,
    reset_db,
    create_db,
    get_db_img_count,
    get_db_list,
    get_db_detailed_list,
    save_db_as,
    save_all_dbs_as,
    save_all_dbs,
    load_all_dbs,
    load_all_dbs_as,
    remove_db,
    is_valid_db,
)