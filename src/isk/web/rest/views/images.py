"""
Image management REST API views.
"""

from abc import ABCMeta
import logging

from aiohttp import web_exceptions

from isk.api import images as images_api
from isk.web.rest.views.db import BaseDBView


logger = logging.getLogger(__name__)


class BaseImagesView(BaseDBView, metaclass=ABCMeta):

    @property
    def requested_image_id(self):
        """Shortcut for extracting image id from request"""
        return int(self.request.match_info.get("image_id", 0))

    async def _get_default_context_data(self):
        data = await super()._get_default_context_data()
        data.get("requested", {}).update(
            {
                "image_id": self.requested_image_id,
            }
        )
        return data


class ImagesListView(BaseImagesView):

    def _get_context_futures(self):
        fs = [
            self.get_images_list(),
        ]
        return fs

    async def get_images_list(self):
        images_list = await self._hit_api(images_api.get_db_img_id_list, self.requested_db_id)
        data = {
            "image_list": images_list,
        }
        return data


class ImageView(BaseImagesView):

    def _get_context_futures(self):
        fs = [
            self.basic_image_data(),
        ]
        return fs

    async def basic_image_data(self):
        image_on_db = await self._hit_api(images_api.is_img_on_db, self.requested_db_id, self.requested_image_id)
        if not image_on_db:
            raise web_exceptions.HTTPNotFound

        data = {
            "exist": image_on_db,
        }
        return data


class ImageKeywordsView(ImageView):

    def _get_context_futures(self):
        fs = [
            self.get_image_keywords_data(),
        ]
        return fs

    async def get_image_keywords_data(self):
        data = await self.basic_image_data()
        keywords = await self._hit_api(images_api.get_keywords_img, self.requested_db_id, self.requested_image_id)
        data.update(
            {
                "keywords": keywords,
            }
        )
        return data
