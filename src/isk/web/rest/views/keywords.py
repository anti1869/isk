"""
Keywords management REST API views.
"""

from abc import ABCMeta

from isk.api import images as images_api
from isk.web.rest.views.generic import BaseDBView


class BaseKeywordsView(BaseDBView, metaclass=ABCMeta):

    @property
    def requested_keyword_id(self):
        """Shortcut for extracting keyword id from request"""
        return int(self.request.match_info.get("keyword_id", 0))

    async def _get_default_context_data(self):
        data = await super()._get_default_context_data()
        data.get("requested", {}).update(
            {
                "keyword_id": self.requested_keyword_id,
            }
        )
        return data


class KeywordsListView(BaseKeywordsView):

    def _get_context_futures(self):
        fs = [
            self.get_keywords_list(),
        ]
        return fs

    async def get_keywords_list(self):
        # TODO: Sometimes this will be implemented
        return {}


class ImagesByKeyword(BaseKeywordsView):

    IMAGES_LIMIT = 100000
    AND_OP = 1

    def _get_context_futures(self):
        fs = [
            self.get_images_by_keyword(),
        ]
        return fs

    async def get_images_by_keyword(self):
        image_list = await self._hit_api(
            images_api.get_all_imgs_by_keywords,
            self.requested_db_id,
            self.IMAGES_LIMIT,
            self.AND_OP,
            (self.requested_keyword_id,)
        )
        data = {
            "image_list": image_list,
        }
        return data
