"""
Image management REST API views.
"""

from abc import ABCMeta
import logging

from aiohttp import web_exceptions

from isk.api import images as images_api
from isk.web.rest.views.db import BaseDBView
from isk.web.rest.views.keywords import BaseKeywordsView


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

    async def delete(self):
        terminator = await self._hit_api(images_api.remove_img, self.requested_db_id, self.requested_image_id)
        assert terminator
        raise web_exceptions.HTTPNoContent


class ImageKeywordsListView(ImageView):

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

    def _get_keyword_id_from_post_data(self, data) -> int:
        try:
            keyword_id = int(data.get("keyword_id", 0))
            assert keyword_id
        except (AssertionError, ValueError):
            logger.error("No keyword id provided in field 'keyword_id'", exc_info=True)
            keyword_id = None
        return keyword_id

    async def post(self):
        data = await self.request.post()
        keyword_id = self._get_keyword_id_from_post_data(data)
        # TODO: Graceful exception resolution here, check for dupes, etc.
        assert await self._hit_api(
            images_api.add_keyword_img, self.requested_db_id, self.requested_image_id, keyword_id
        )
        raise web_exceptions.HTTPNoContent

    async def delete(self):
        # TODO: Graceful error handling needs to be done here also
        assert await self._hit_api(
            images_api.remove_all_keyword_img,
            self.requested_db_id,
            self.requested_image_id
        )
        raise web_exceptions.HTTPNoContent


class ImageKeywordView(BaseKeywordsView, ImageView):

    def _get_context_futures(self):
        fs = [
            self.check_keyword_exist(),
        ]
        return fs

    async def check_keyword_exist(self):
        keywords = set(
            await self._hit_api(images_api.get_keywords_img, self.requested_db_id, self.requested_image_id)
        )
        if self.requested_keyword_id not in keywords:
            raise web_exceptions.HTTPNotFound

        data = {
            "image_has_keyword": True,
        }
        return data

    async def delete(self):
        # TODO: Graceful error handling needs to be done here
        assert await self._hit_api(
            images_api.remove_keyword_img,
            self.requested_db_id,
            self.requested_image_id,
            self.requested_keyword_id
        )

        raise web_exceptions.HTTPNoContent
