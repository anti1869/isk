"""
DB Management REST API views.
"""

from abc import ABCMeta, abstractmethod
import asyncio

from sunhead.rest.views import JSONView

from isk.api import db as db_api
from isk.api.executor import isk_api_executor


class BaseDBView(JSONView, metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = asyncio.get_event_loop()

    def _get_default_context_futures(self) -> list:
        return []

    @abstractmethod
    def _get_context_futures(self) -> list:
        return []

    async def _get_context_data(self) -> dict:
        fs = self._get_default_context_futures() + self._get_context_futures()
        data = {}
        if not len(fs):
            return data

        for f in asyncio.as_completed(fs):
            result = await f
            data.update(result)

        return data

    async def get(self):
        ctx = await self._get_context_data()
        return self.json_response(context_data=ctx)


class DBListView(BaseDBView):

    async def get_db_list(self) -> dict:
        db_list = await self._loop.run_in_executor(isk_api_executor, db_api.get_db_detailed_list)
        data = {
            "databases_list": db_list,
        }
        return data

    def _get_context_futures(self):
        fs = [
            self.get_db_list()
        ]
        return fs

