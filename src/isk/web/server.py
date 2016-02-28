"""
Web server worker implementation. Based on SunHead framework, which is in turn based on aiohttp web server.
"""

from sunhead.workers.http.server import Server


class IskHTTPServer(Server):

    @property
    def app_name(self):
        return "IskHTTPServer"


