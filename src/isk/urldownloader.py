###############################################################################
# begin                : Sun Aug  6, 2006  4:58 PM
# copyright            : (C) 2012 by Ricardo Niederberger Cabral,
#                      : (C) 2016 Dmitry Litvinenko
# email                : ricardo dot cabral at imgseek dot net
#                      : anti1869@gmail.com
#
###############################################################################
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###############################################################################

import asyncio
import logging

import aiohttp

from sunhead.conf import settings


logger = logging.getLogger(__name__)


CHUNK_SIZE = 2048


# This is expected by Ricardo's old code.
# Probably will remove it later.
def url_to_file(url, destfile) -> bool:
    """Entrypoint from blocking code"""

    loop = asyncio.get_event_loop()
    local_path = loop.run_until_complete(
        download_image(url, destfile)
    )
    return bool(local_path)


async def download_image(url: str, local_path: str = None, safe: bool = True) -> str:
    """
    Download image file and return its full path. If path is already exist, it will be overwritten.

    :param url: Url to download
    :param local_path: Path on local filesystem to download to.
    :param safe: If True, will not raise error, instead will return None if there are any troubles.
    :return: Path to downloaded file.
    """

    # TODO: Use async fileio
    # TODO: Check url or downloaded file is actually an image
    try:
        with open(local_path, 'wb') as fd:
            async with aiohttp.get(url) as resp:  # fixme: add timeout
                assert resp.status == 200
                while True:
                    chunk = await resp.content.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    fd.write(chunk)
    except (AssertionError, aiohttp.errors.ClientError, asyncio.TimeoutError, OSError, IOError):
        logger.error("Can't download url '%s' to path '%s", url, local_path, exc_info=True)
        if not safe:
            raise
        local_path = None

    return local_path
