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

import aiohttp

from urllib.request import urlopen, Request
from sunhead.conf import settings
import logging

rootLog = logging.getLogger('urldownloader')


def url_to_file(theurl, destfile):
    """Entrypoint from blocking code"""
    data = urlData(theurl)
    if not data:
        return False

    f = open(destfile, 'wb')
    f.write(data)
    f.close()
    return True


def urlData(theurl):
    if not theurl:
        return None
    if len(theurl) < 12:
        return None
    if theurl[:7].lower() != 'http://':
        return None

    txdata = None  # if we were making a POST type request, we could encode a dictionary of values here - using urllib.urlencode
    txheaders = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7)', 'Referer': theurl}

    try:
        req = Request(theurl, txdata, txheaders)  # create a request object
        timeout = settings.core.getint('daemon', 'urlDownloaderTimeout')
        handle = urlopen(req, timeout=timeout)  # and open it to return a handle on the url
        data = handle.read()
        return data
    except Exception as e:
        rootLog.error(e)
        return False

async def download_image(url: str, local_path: str = None) -> str:
