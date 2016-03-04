"""
JSON-RPC 2.0 interface to all exposed Isk APIs. (See http://www.jsonrpc.org/specification)

It's now working at /jsonrpc/ endpoint. POST calls to that address. Example usage:

..code-block:: python

    import requests
    import json


    ep = "http://localhost:31128/jsonrpc/"
    headers = {'content-type': 'application/json'}


    def hit_api(method, *args):
        payload = {
            "method": method,
            "params": list(args),
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(ep, data=json.dumps(payload), headers=headers)
        return response.json().get("result")


    def test():
        db_list = hit_api("get_db_list")
        image_list = hit_api("get_db_img_id_list", db_list[0])
        similar_images = hit_api("query_img_id", db_list[0], image_list[0])

        print(similar_images)

    if __name__ == "__main__":
        test()

Use this RPC instead of REST API interface, if you need more control over Isk.
"""

from itertools import chain
import logging

from jsonrpc import JSONRPCResponseManager, dispatcher
from jsonrpc.exceptions import JSONRPCServerError, JSONRPCException

from sunhead.rest.views import BasicView

from isk.api.db import exporting as db_exporting
from isk.api.images import exporting as images_exporting
from isk.api.runtime import exporting as runtime_exporting
from isk.exceptions import IskHttpServerException


logger = logging.getLogger(__name__)


def get_jsonrpc_dispatcher():
    for method in chain(db_exporting, images_exporting, runtime_exporting):
        dispatcher[method.__name__] = method
    return dispatcher


class JSONRPCView(BasicView):

    async def post(self):
        dispatcher = self.request.app.get("jsonrpc_dispatcher", None)
        if dispatcher is None:
            raise IskHttpServerException("JSONRPC dispatcher not found. Place it in server app")

        request_text = await self.request.text()

        # TODO: Make this non-blocking
        # TODO: Meaningful error handling of JSON-RPC calls
        try:
            response = JSONRPCResponseManager.handle(request_text, dispatcher)
        except Exception:
            response = JSONRPCServerError()
            logger.error("JSON-RPC Error", exc_info=True)

        return self.basic_response(text=response.json, content_type="application/json")


urlconf = (
    ("POST", "/", JSONRPCView),
)
