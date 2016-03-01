###############################################################################
# begin                : Sun Jan  8 21:24:38 BRST 2012
# copyright            : (C) 2012 by Ricardo Niederberger Cabral,
#                      : (C) 2016 Dmitry Litvinenko
# email                : ricardo dot cabral at imgseek dot net
#                      : anti1869@gmail.com
#
###############################################################################
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###############################################################################

from configparser import SafeConfigParser
import logging
from logging.config import dictConfig
import os
import tempfile
#
# logger = logging.getLogger(__name__)
#
# # Defaults
# core = SafeConfigParser(
#     {
#         'startAsDaemon': 'false',  # run as background process on UNIX systems
#         'basePort': '31128',  # base tcp port to start listening at for HTTP requests
#         'debug': 'true',  # print debug messages to console
#         'saveAllOnShutdown': 'true',  # automatically save all database spaces on server shutdown
#         'databasePath': "~/isk-db",  # file where to store database files
#         'saveInterval': '120',  # seconds between each automatic database save
#         'automaticSave': 'false',  # whether the database should be saved automatically
#         'isClustered': 'false',  # run in cluster mode ? If True, make sure subsequent settings are ok
#         'seedPeers': 'isk2host:31128',
#         'bindHostname': 'isk1host',  # hostname for this instance. Other instances may try to connect to this hostname
#         'logPath': 'isk-daemon.log',
#         'logDebug': 'true',
#         'urlDownloaderTimeout': '10',  # timeout in seconds for downloading images from web
#     }
# )

CONFIG_FILENAME = "isk.conf"
COMMON_PLACES = (
    CONFIG_FILENAME,
    os.path.expanduser('~/{}'.format(CONFIG_FILENAME)),
    "/etc/isk/{}".format(CONFIG_FILENAME),
    # os.path.join(os.environ.get("ISK_CONFIG"), CONFIG_FILENAME),
)

HOST = "0.0.0.0"
PORT = 31128
DEBUG = True
SAVE_ALL_ON_SHUTDOWN = True
DATABASE_PATH = "~/isk-db"
SAVE_INTERVAL = 120
AUTOMATIC_SAVE = False
BIND_HOSTNAME = "isk1host"
LOG_PATH = "isk-daemon.log"
LOG_DEBUG = False
URL_DOWNLOADER_TIMEOUT = 10

DEBUG_AUTORELOAD_APP = True
TMP_DIR = tempfile.gettempdir()

#
# # read from many possible locations
# conffile = core.read(COMMON_PLACES)
#
# for sec in ('database', 'daemon', 'cluster'):
#     if not core.has_section(sec):
#         core.add_section(sec)
#
# # perform some clean up/bulletproofing
# core.set('database', 'databasePath', os.path.expanduser(core.get('database', 'databasePath')))
#
# # fix windows stuff
# if os.name == 'nt':  # fix windows stuff
#     core.set('database', 'databasePath', os.path.expanduser(core.get('database', 'databasePath').replace('/', '\\')))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s%(levelname)-8s%(reset)s %(blue)s[%(name)s:%(lineno)s] %(white)s%(message)s"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

# dictConfig(LOGGING)
#
# if len(conffile) < 1:
#     logger.warning(
#         'No config file (%s) found. '
#         'Looked at %s '
#         'Using defaults for everything.',
#         CONFIG_FILENAME,
#         COMMON_PLACES,
#     )
# else:
#     logger.info('Using config file "%s"' % conffile[0])
