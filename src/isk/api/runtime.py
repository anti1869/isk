"""
Runtime API
"""


import time

from isk import settings, statistics
from isk.api.db import backend


def get_isk_log(window=30):
    """
    Returns the last lines of text in the iskdaemon instance log

    :type  window: number
    :param window: number of lines to retrieve

    :rtype:   string
    :return:  text block
    :since: 0.9.3
    """
    from isk.utils import tail

    return tail(open(settings.core.get('daemon', 'logPath')), window)


def get_global_server_stats():
    """
    Return the most similar images to the supplied one.

    :rtype:   map

    :since: 0.7
    :return:  key is stat name, value is value.
        Keys are ['isk-daemon uptime', 'Number of databases', 'Total memory usage', 'Resident memory usage',
        'Stack memory usage']
    """

    stats = {}

    stats['isk-daemon uptime'] = statistics.human_readable(time.time() - daemon_start_time)
    stats['Number of databases'] = len(backend.get_db_list())
    stats['Total memory usage'] = statistics.memory()
    stats['Resident memory usage'] = statistics.resident()
    stats['Stack memory usage'] = statistics.stacksize()

    return stats


def shutdown_server():
    """
    Request a shutdown of this server instance.

    :rtype:   number

    :since: 0.7
    :return:  always M{1}
    """
    raise NotImplementedError


    #
    # global has_shutdown
    #
    # if has_shutdown:
    #     return 1  # already went through a shutdown
    #
    # if settings.core.getboolean('daemon','saveAllOnShutdown'):
    #     save_all_dbs()
    #     backend.closedb()
    #
    # logger.info("Shuting instance down...")
    # # from twisted.internet import reactor
    # # reactor.callLater(1, reactor.stop)
    # has_shutdown = True
    # return 1


exporting = (
    get_isk_log,
    get_global_server_stats,
    shutdown_server,
)
