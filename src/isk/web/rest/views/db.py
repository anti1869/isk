"""
DB Management REST API views.
"""

from aiohttp import web_exceptions

from isk.api import db as db_api
from isk.web.rest.views.generic import BaseDBView


class DBListView(BaseDBView):

    def _get_context_futures(self):
        fs = [
            self.get_db_list(),
        ]
        return fs

    async def make_new_db_id(self):
        id_list = await self._hit_api(db_api.get_db_list)
        new_id = max(id_list) + 1
        return new_id

    async def post(self):
        new_db_id = await self.make_new_db_id()
        created_id = await self._hit_api(db_api.create_db, new_db_id)
        assert created_id == new_db_id
        await self._hit_api(db_api.save_all_dbs)
        new_url = "./{}/".format(new_db_id)  # FIXME: Use reverse url resolving here
        return self.created_response(location=new_url)


class DBView(BaseDBView):

    async def get_db_info(self):
        db_list = await self.get_db_list()
        if self.requested_db_id not in db_list["databases_list"]:
            raise web_exceptions.HTTPNotFound

        image_count = await self._hit_api(db_api.get_db_img_count, self.requested_db_id)
        data = {
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
        terminator = await self._hit_api(db_api.remove_db, self.requested_db_id)
        assert terminator
        raise web_exceptions.HTTPNoContent


class DBResetView(BaseDBView):

    def _get_context_futures(self):
        return []

    async def post(self):
        assert await self._hit_api(db_api.reset_db, self.requested_db_id)
        await self._hit_api(db_api.save_all_dbs)
        raise web_exceptions.HTTPNoContent
