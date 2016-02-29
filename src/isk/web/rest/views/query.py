"""
Search Queries API.
"""

from abc import ABCMeta

from aiohttp import web_exceptions

from isk.api import images as images_api
from isk.web.rest.views.db import BaseDBView


DEFAULT_RESULTS = 20


class BaseQueryView(BaseDBView, metaclass=ABCMeta):

    @property
    def requested_image_id(self):
        """Shortcut for extracting image id from request"""
        return int(self.request.GET.get("image_id", 0))

    @property
    def requested_results(self):
        return int(self.request.GET.get("results", DEFAULT_RESULTS))

    async def _get_default_context_data(self):
        data = await super()._get_default_context_data()
        data.get("requested", {}).update(
            {
                "image_id": self.requested_image_id,
            }
        )
        return data


class SimilarImagesQuery(BaseQueryView):

    def _get_context_futures(self):
        fs = [
            self.get_similar_images(),
        ]
        return fs

    async def get_similar_images(self):
        if self.requested_image_id:
            images_list = await self._hit_api(
                images_api.query_img_id,
                self.requested_db_id,
                self.requested_image_id,
                self.requested_results
            )
        else:
            images_list = tuple()

        data = {
            "results": images_list,
        }
        return data

    async def post(self):
        raise NotImplementedError
