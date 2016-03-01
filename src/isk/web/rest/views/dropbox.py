"""
Image dropbox - adding images to DB in numerous ways.
"""

from abc import ABCMeta, abstractmethod
import asyncio
import logging
import os
import tarfile
import tempfile
from typing import Iterable, Sequence
from urllib.parse import urlsplit

from aiohttp import web_exceptions

from sunhead.conf import settings

from isk.api import images as images_api, db as db_api
from isk.urldownloader import download_image
from isk.web.rest.views.db import BaseDBView


logger = logging.getLogger(__name__)


class ImagesDropbox(BaseDBView, metaclass=ABCMeta):

    CHUNK = 2048
    EOF_MARKER = b''


    @abstractmethod
    async def add_image(self):
        pass

    def _get_context_futures(self):
        return []

    async def post(self):
        # asyncio.ensure_future(  # TODO: Test for large requests and fallback to await may be
        #     self.add_image()
        # )
        await self.add_image()
        raise web_exceptions.HTTPAccepted

    def _get_image_id_from_post_data(self, data) -> int:
        try:
            image_id = int(data.get("image_id", 0))
            assert image_id
        except (AssertionError, ValueError):
            logger.error("No image id provided in field 'image_id'", exc_info=True)
            return

    async def _body_to_file(self, filename: str) -> None:
        with open(filename, 'wb') as f:
            while True:
                chunk = await self.request.content.readany()
                f.write(chunk)
                if chunk is self.EOF_MARKER:
                    break


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

    TMP_FILE_NAME = "archive.tgz"

    async def add_image(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmppath = os.path.join(tmpdirname, self.TMP_FILE_NAME)
            await self._body_to_file(tmppath)
            await self._unarchive(tmppath, cleanup=True)
            added = await self._hit_api(images_api.add_dir, self.requested_db_id, tmpdirname, True, True)
            logger.info("Added %s file(s) from uploaded archive", added)
        await self._hit_api(db_api.save_all_dbs)

    async def _unarchive(self, archive_path: str, cleanup: bool = True) -> None:
        dest = os.path.dirname(archive_path)
        with tarfile.open(archive_path) as tar:
            tar.extractall(path=dest, members=self._unarchive_members(tar))
        if cleanup:
            os.remove(archive_path)

    def _unarchive_members(self, members: Sequence) -> Iterable:
        for tarinfo in members:
            try:
                name, ext = os.path.splitext(tarinfo.name)
                ext = ext.split(".")[1]
                assert int(name) > 0
                if ext in images_api.SUPPORTED_IMAGE_EXTENSIONS:
                    yield tarinfo
            except (ValueError, IndexError, AssertionError):
                # Unsupported file
                pass
