"""
Image dropbox - adding images to DB in numerous ways.
"""

from abc import ABCMeta, abstractmethod
import asyncio
import logging
import os
from urllib.parse import urlsplit

from aiohttp import web_exceptions

from sunhead.conf import settings

from isk.api import images as images_api
from isk.urldownloader import download_image
from isk.web.rest.views.db import BaseDBView


logger = logging.getLogger(__name__)


class ImagesDropbox(BaseDBView, metaclass=ABCMeta):

    @abstractmethod
    async def add_image(self):
        pass

    async def post(self):
        asyncio.ensure_future(
            self.add_image()
        )
        raise web_exceptions.HTTPAccepted

    def _get_image_id_from_post_data(self, data) -> int:
        try:
            image_id = int(data.get("image_id", 0))
            assert image_id
        except (AssertionError, ValueError):
            logger.error("No image id provided in field 'image_id'", exc_info=True)
            return


class ImagesDropboxUrl(ImagesDropbox):

    async def add_image(self) -> None:
        data = await self.request.post()
        url = data["download_url"]
        image_id = self._get_image_id_from_post_data(data)
        logger.debug("Adding from download_url=%s", url)
        filename = os.path.basename(urlsplit(url).path)  # Or we can use tmpfile here
        local_path = os.path.join(settings.TMP_DIR, filename)  # FIXME: remove tmp file after add
        downloaded_path = await download_image(url, local_path)
        if not downloaded_path:
            logger.error("Image is not added from url '%s'", url)
            return

        result = await self._hit_api(images_api.add_img, self.requested_db_id, image_id, downloaded_path)
        assert result
        logger.info("Added id=%s from url %s", image_id, url)


class ImagesDropboxFile(ImagesDropbox):

    async def add_image(self):
        data = await self.request.post()  # FIXME: Do not read whole file into memory, use resp.content
        image_field = data["image"]
        image_id = self._get_image_id_from_post_data(data)
        logger.debug("Adding from image filename=%s", image_field.filename)
        local_path = os.path.join(settings.TMP_DIR, image_field.filename)
        with open(local_path, 'wb') as f:
            for l in image_field.file:
                f.write(l)

        result = await self._hit_api(images_api.add_img, self.requested_db_id, image_id, local_path)
        assert result
        logger.debug("Added id=%s", image_id)


class ImagesDropboxArchive(ImagesDropbox):

    async def add_image(self):
        pass
        # archive_field = data["archive"]
        # logger.info("Adding from archive filename=%s", archive_field.filename)
