"""
DB Management REST API views.
"""

from abc import ABCMeta, abstractmethod
import asyncio
from datetime import datetime
from functools import partial
from typing import Callable, Any

from aiohttp import web_exceptions

from sunhead.rest.views import JSONView

from isk.api import db as db_api
from isk.api.executor import isk_api_executor


def time_taken(f):
    """
    Adds "time_taken" key to the dict, returned by wrapped function.
    """
    async def _wrapper(*args, **kwargs) -> dict:
        d1 = datetime.now()
        result = await f(*args, **kwargs)
        d2 = datetime.now()
        delta = d2 - d1
        result["time_taken"] = delta.total_seconds()
        return result
    return _wrapper



class BaseDBView(JSONView, metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = asyncio.get_event_loop()

    def _get_default_context_futures(self) -> list:
        fs = [
            self._get_default_context_data(),
        ]
        return fs

    async def _get_default_context_data(self):
        data = {
            "requested": {
                "db_id": self.requested_db_id,
            }
        }
        return data

    async def get_db_list(self) -> dict:
        db_list = await self._loop.run_in_executor(isk_api_executor, db_api.get_db_detailed_list)
        data = {
            "databases_list": db_list,
        }
        return data

    @abstractmethod
    def _get_context_futures(self) -> list:
        return []

    @property
    def requested_db_id(self):
        """Shortcut for extracting db id from request"""
        return int(self.request.match_info.get("db_id", 0))

    async def _hit_api(self, func: Callable, *args) -> Any:
        """
        Wrap API call into executor. Saves some typing.

        :param func: API Function to run
        :param args: Arguments to that function
        :return: Result of the function
        """
        fetcher = partial(func, *args)
        result = await self._loop.run_in_executor(isk_api_executor, fetcher)
        return result

    @time_taken
    async def _get_context_data(self) -> dict:
        fs = self._get_default_context_futures() + self._get_context_futures()
        data = {}
        if not len(fs):
            return data

        for f in asyncio.as_completed(fs):
            result = await f
            if result is not None:
                data.update(result)

        return data

    async def get(self):
        ctx = await self._get_context_data()
        return self.json_response(context_data=ctx)


class DBListView(BaseDBView):

    def _get_context_futures(self):
        fs = [
            self.get_db_list(),
        ]
        return fs

    async def make_new_db_id(self):
        id_list = await self._loop.run_in_executor(isk_api_executor, db_api.get_db_list)
        new_id = max(id_list) + 1
        return new_id

    async def post(self):
        new_db_id = await self.make_new_db_id()
        db_creator = partial(db_api.create_db, new_db_id)
        created_id = await self._loop.run_in_executor(isk_api_executor, db_creator)
        assert created_id == new_db_id
        await self._loop.run_in_executor(isk_api_executor, db_api.save_all_dbs)
        new_url = "./{}/".format(new_db_id)
        return self.created_response(location=new_url)


class DBView(BaseDBView):

    async def get_db_info(self):
        db_list = await self.get_db_list()
        if self.requested_db_id not in db_list["databases_list"]:
            raise web_exceptions.HTTPNotFound

        counter = partial(db_api.get_db_img_count, self.requested_db_id)
        image_count = await self._loop.run_in_executor(isk_api_executor, counter)
        data = {
            "requested_db_id": self.requested_db_id,
            "db_info": db_list["databases_list"].get(self.requested_db_id, {}),
            "image_count": image_count,
        }
        return data

    def _get_context_futures(self):
        fs = [
            self.get_db_info(),
        ]
        return fs

    async def delete(self):
        terminator = partial(db_api.remove_db, self.requested_db_id)
        result = await self._loop.run_in_executor(isk_api_executor, terminator)
        assert result
        raise web_exceptions.HTTPNoContent
