"""
Web server worker implementation. Based on SunHead framework, which is in turn based on aiohttp web server.
"""

import logging

from aiocron import crontab

from sunhead.conf import settings
from sunhead.workers.http.server import Server

from isk.api.db import save_all_dbs
from isk.web.rest.urls import urlconf as rest_urlconf

logger = logging.getLogger(__name__)


REST_URL_PREFIX = "/api/1.0"


class IskHTTPServer(Server):

    @property
    def app_name(self):
        return "IskHTTPServer"

    def _map_to_prefix(self, urlprefix: str, urlconf: tuple) -> tuple:
        mapped = ((method, urlprefix + url, view) for method, url, view in urlconf)
        return tuple(mapped)

    def get_urlpatterns(self):
        urls = self._map_to_prefix(REST_URL_PREFIX, rest_urlconf)
        return urls

    def init_requirements(self, loop):
        super().init_requirements(loop)
        periodic_db_saver = crontab(settings.PERIODIC_DB_SAVE_CRONTAB, self._periodic_dbs_save, start=False)
        periodic_db_saver.start()

    def cleanup(self, *args, **kwargs):
        super().cleanup(*args, **kwargs)
        num = save_all_dbs()
        logger.info("%s databases saved on exit", num)

    async def _periodic_dbs_save(self):
        num = save_all_dbs()
        logger.debug("Periodic DB save. %s spaces saved", num)
