"""
Web server worker implementation. Based on SunHead framework, which is in turn based on aiohttp web server.
"""

from sunhead.workers.http.server import Server

from isk.web.rest.urls import urlconf as rest_urlconf


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
