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

import logging
import os
import time
from typing import Sequence, List, Tuple, Iterable

from isk import utils

try:
    from isk.backends.imgseeklib import imgdb
except ImportError:
    logging.error(
        "Unable to load the C++ extension '_imgdb.so(pyd)' module. "
        "See http://www.spacesortabs.com/isk/installing/",
        exc_info=True
    )
    raise

logger = logging.getLogger(__name__)

# to help determining img format from extension
SUPPORTED_IMG_EXTS = {
    'jpeg', 'jpg', 'gif', 'png', 'rgb', 'jpe', 'pbm', 'pgm', 'ppm', 'tiff', 'tif', 'rast', 'xbm', 'bmp'
}


class DBSpace(object):

    INFO_ATTRS = (
        "id", "query_count", "last_query_per_min", "query_min_count", "query_min_cur", "last_add_per_min",
        "add_min_count", "add_min_cur", "add_count", "add_since_last_save", "last_id", "last_save_time",
        "file_name",
    )

    def __init__(self, id):

        for attr_name in self.INFO_ATTRS:
            setattr(self, attr_name, 0)

        # Overload some of them
        self.id = id
        self.last_id = 1
        self.file_name = "not yet saved"  # currently loaded data file

        if not imgdb.isValidDB(id):  # only init if needed
            logger.debug("New dbSpace requires init: %d" % id)
            imgdb.initDbase(id)

    def get_stats(self):
        data = {
            name: getattr(self, name) for name in self.INFO_ATTRS
        }
        return data

    def __str__(self):
        reprs = "DPSpace ; "
        for key in dir(self):
            if not key.startswith('__'):
                value = getattr(self, key)
                if not callable(value):
                    reprs += key + "=" + str(value) + "; "
        return reprs

        # Original Ricardo's comment:
        # """
        # # not refactoring all ImgDB fcns into here in order to save some function calls
        # So this class is in a sense a mere data structure.
        #
        # def postLoad(self):
        #     # adjust last added image id
        #     self.lastId = self._imgdb.getImageCount(self.id) + 1
        #     log.info('Database loaded: ' + self)
        # """


def safe_str(obj):
    """ Return the byte string representation of obj """
    return str(obj)
    # try:
    #     return str(obj)
    # except UnicodeEncodeError:
    #     # obj is unicode
    #     return unicode(obj).encode('unicode_escape')


def add_count(db_space: DBSpace) -> None:
    # add per minutes counting
    db_space.add_count += 1
    if time.localtime()[4] > db_space.add_min_cur:
        db_space.add_min_cur = time.localtime()[4]
        db_space.last_add_per_min = db_space.add_min_count
    else:
        db_space.add_min_count += 1


def count_query(db_space: DBSpace) -> None:
    db_space.query_count += 1
    if time.localtime()[4] > db_space.query_min_cur:
        db_space.query_min_cur = time.localtime()[4]
        db_space.last_query_per_min = db_space.query_min_count
    else:
        db_space.query_min_count += 1


class ImgDB(object):
    def __init__(self, automatic_save, save_interval):
        self.db_spaces = {}
        self.globalFileName = 'global-imgdb-not-saved-yet'
        # global statistics
        self._automatic_save = automatic_save
        self._save_interval = save_interval

    @property
    def supported_image_extensions(self) -> set:
        return set(SUPPORTED_IMG_EXTS)

    @utils.dump_args
    def createdb(self, db_id) -> int:
        if db_id in self.db_spaces:
            logger.warn('Replacing existing database id: %s', str(db_id))
        self.db_spaces[db_id] = DBSpace(db_id)
        self.resetdb(db_id)
        return db_id

    @utils.dump_args
    def closedb(self):
        return imgdb.closeDbase()

    @utils.require_known_db_id
    @utils.dump_args
    def resetdb(self, db_id) -> bool:
        if imgdb.resetdb(db_id):  # succeeded
            self.db_spaces[db_id] = DBSpace(db_id)
            logger.debug("resetdb() ok")
            return True
        return False

    @utils.dump_args
    def loaddb(self, db_id, fname) -> int:
        if imgdb.resetdb(db_id):
            logger.warn('Load is replacing existing database id:' + str(db_id))
        dbSpace = DBSpace(db_id)
        self.db_spaces[db_id] = dbSpace
        dbSpace.file_name = fname

        if not imgdb.loaddb(db_id, fname):
            logger.error("Error loading image database")
            del self.db_spaces[db_id]
            return None
        # adjust last added image id
        logger.info('| Database loaded: ' + str(dbSpace))
        dbSpace.last_id = self.get_img_count(dbSpace.id) + 1
        return db_id

    @utils.require_known_db_id
    @utils.dump_args
    def savedb(self, db_id: int) -> bool:
        result = bool(imgdb.savedb(db_id, self.db_spaces[db_id].file_name))
        return result

    @utils.require_known_db_id
    @utils.dump_args
    def savedbas(self, db_id: int, fname: str) -> bool:
        if not imgdb.savedb(db_id, fname):
            logger.error("Error saving image database")
            return False

        dbSpace = self.db_spaces[db_id]
        dbSpace.last_save_time = time.time()
        dbSpace.file_name = fname
        logger.info('| Database id=%s saved to "%s"' % (dbSpace, fname))
        return True

    @utils.dump_args
    def loadalldbs(self, fname) -> int:
        try:
            dbCount = imgdb.loadalldbs(fname)
            for dbid in self.get_db_list():
                self.db_spaces[dbid] = DBSpace(dbid)
                self.db_spaces[dbid].lastId = self.get_img_count(dbid) + 1
            logger.debug('| Database (%s) loaded with %d spaces' % (fname, dbCount))
            self.globalFileName = fname
            return dbCount
        except RuntimeError as e:
            logger.error(e)
            return 0

    @utils.dump_args
    def savealldbs(self, fname=None) -> int:
        if not fname:
            fname = self.globalFileName
        res = imgdb.savealldbs(fname)
        if not res:
            logger.error("Error saving image database")
            return res
        logger.info('| All database spaces saved at "%s"' % fname)
        return res

    @utils.require_known_db_id
    @utils.dump_args
    def add_dir(self, dbId, path, recurse, fname_as_id=False):

        path = safe_str(path)
        addedCount = 0
        dbSpace = self.db_spaces[dbId]
        if not os.path.isdir(path):
            logger.error("'%s' does not exist or is not a directory" % path)
            return 0
        for fil in os.listdir(path):
            fil = safe_str(fil)
            fil = path + os.sep + fil
            if len(fil) > 4 and fil.split('.')[-1].lower() in SUPPORTED_IMG_EXTS:
                file_name = os.path.splitext(os.path.basename(fil))[0]
                image_id = dbSpace.lastId

                # If ``fname_as_id`` is True, try to retrieve image id from filename.
                if fname_as_id:
                    try:
                        image_id = int(file_name)
                    except ValueError:
                        logger.warning("Can not get id from filename {}. Skipping".format(file_name))
                        continue

                # Add image to db
                try:
                    addedCount += self.add_image(dbId, fil, image_id)
                except RuntimeError as e:
                    logger.error(e)

            elif recurse and os.path.isdir(fil):
                addedCount += self.add_dir(dbId, fil, recurse, fname_as_id)
        return addedCount

    @utils.require_known_db_id
    @utils.dump_args
    def remove_db(self, db_id) -> bool:
        if imgdb.removedb(db_id):
            del self.db_spaces[db_id]
            return True
        return False

    @utils.require_known_db_id
    @utils.dump_args
    def add_image_blob(self, dbId, data, newid=None):
        dbSpace = self.db_spaces[dbId]

        if not newid:
            newid = dbSpace.lastId

        newid = newid
        add_count(dbSpace)
        # call imgdb
        res = imgdb.addImageBlob(dbId, newid, data)

        if res != 0:  # add successful
            dbSpace.lastId = newid + 1
            # time to save automatically ?
            # TODO this should be a reactor timer
            if self._automatic_save and time.time() - dbSpace.lastSaveTime > self._save_interval:
                dbSpace.lastSaveTime = time.time()
                self.savealldbs()
        return res

    @utils.require_known_db_id
    @utils.dump_args
    def add_image(self, db_id, fname, newid=None) -> bool:
        dbSpace = self.db_spaces[db_id]

        if not newid:
            newid = dbSpace.lastId

        newid = newid
        add_count(dbSpace)
        # call imgdb
        res = imgdb.addImage(db_id, newid, fname)

        if res != 0:  # add successful
            dbSpace.lastId = newid + 1
            # time to save automatically ?            
            if self._automatic_save and time.time() - dbSpace.lastSaveTime > self._save_interval:
                dbSpace.lastSaveTime = time.time()
                self.savealldbs()
        return bool(res)

    @utils.require_known_db_id
    @utils.dump_args
    def remove_img(self, db_id, id) -> bool:
        # TODO should also call the code that saves db after a number of ops
        return bool(imgdb.removeID(db_id, id))

    def get_db_detailed_list(self) -> dict:
        db_id_list = self.get_db_list()
        detlist = {
            db_id: self.db_spaces[db_id].get_stats() for db_id in db_id_list
        }
        return detlist

    @utils.require_known_db_id
    def is_image_on_db(self, db_id, id):
        return imgdb.isImageOnDB(db_id, id)

    @utils.require_known_db_id
    def calc_avgl_diff(self, dbId, id1, id2):
        return imgdb.calcAvglDiff(dbId, id1, id2)

    @utils.require_known_db_id
    def calc_diff(self, dbId, id1, id2):
        return imgdb.calcDiff(dbId, id1, id2)

    @utils.require_known_db_id
    def get_image_dimensions(self, dbId, id):
        return [imgdb.getImageWidth(dbId, id), imgdb.getImageHeight(dbId, id)]

    @utils.require_known_db_id
    def get_image_avgl(self, dbId, id):
        return imgdb.getImageAvgl(dbId, id)

    @utils.require_known_db_id
    def getIdsBloomFilter(self, dbId):
        return imgdb.getIdsBloomFilter(dbId)

    @utils.require_known_db_id
    def get_img_count(self, db_id) -> int:
        return imgdb.getImgCount(db_id)

    @utils.require_known_db_id
    def get_img_id_list(self, db_id) -> tuple:
        id_list = imgdb.getImgIdList(db_id)
        return id_list

    def is_valid_db(self, db_id) -> bool:
        return imgdb.isValidDB(db_id)

    def get_db_list(self) -> tuple:
        return imgdb.getDBList()

    @utils.require_known_db_id
    def get_query_count(self, dbId):
        return self.db_spaces[dbId].queryCount

    @utils.require_known_db_id
    def get_query_per_min_count(self, dbId):
        return self.db_spaces[dbId].lastQueryPerMin

    @utils.require_known_db_id
    def get_add_count(self, dbId):
        return self.db_spaces[dbId].addCount

    @utils.require_known_db_id
    def get_add_per_min_count(self, dbId):
        return self.db_spaces[dbId].lastAddPerMin

    @utils.require_known_db_id
    @utils.dump_args
    def add_keyword_img(self, db_id: int, image_id: int, keyword_id: int) -> bool:
        return imgdb.addKeywordImg(db_id, image_id, keyword_id)

    @utils.require_known_db_id
    def get_cluster_keywords(self, dbId, numClusters, keywords):
        return imgdb.getClusterKeywords(dbId, numClusters, keywords)

    @utils.require_known_db_id
    def get_cluster_db(self, dbId, numClusters):
        return imgdb.getClusterDb(dbId, numClusters)

    @utils.require_known_db_id
    def get_keywords_popular(self, dbId, numres):
        return imgdb.getKeywordsPopular(dbId, numres)

    @utils.require_known_db_id
    def get_keywords_visual_distance(self, dbId, distanceType, keywords):
        return imgdb.getKeywordsVisualDistance(dbId, distanceType, keywords)

    @utils.require_known_db_id
    def get_all_imgs_by_keywords(self, db_id, numres, kw_join_type, keywords) -> list:
        return imgdb.getAllImgsByKeywords(db_id, numres, kw_join_type, keywords)

    @utils.require_known_db_id
    def query_img_id_fast_keywords(self, dbId, imgId, numres, kwJoinType, keywords):
        return imgdb.queryImgIDFastKeywords(dbId, imgId, numres, kwJoinType, keywords)

    @utils.require_known_db_id
    def query_img_id_keywords(self, dbId, imgId, numres, kwJoinType, keywords, fast=False):
        dbSpace = self.db_spaces[dbId]

        # return [[resId,resRatio]]
        # update internal counters
        numres = int(numres) + 1
        count_query(dbSpace)

        # do query
        results = imgdb.queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywords, fast)

        res = self._normalize_results(results)

        logger.debug("queryImgIDKeywords() ret=" + str(res))
        return res

    @utils.require_known_db_id
    def most_popular_keywords(self, dbId, imgs, excludedKwds, count, mode):
        res = imgdb.mostPopularKeywords(dbId, imgs, excludedKwds, count, mode)
        logger.debug("mostPopularKeywords() ret=" + str(res))
        return res

    @utils.require_known_db_id
    def get_keywords_img(self, dbId, imgId):
        res = imgdb.getKeywordsImg(dbId, imgId)
        logger.debug("getKeywordsImg() ret=" + str(res))
        return res

    @utils.require_known_db_id
    @utils.dump_args
    def remove_all_keywords_img(self, db_id: int, image_id: int) -> bool:
        return imgdb.removeAllKeywordImg(db_id, image_id)

    @utils.require_known_db_id
    @utils.dump_args
    def remove_keyword_img(self, db_id: int, image_id: int, keyword_id: int) -> bool:
        return imgdb.removeKeywordImg(db_id, image_id, keyword_id)

    @utils.require_known_db_id
    @utils.dump_args
    def add_keywords_img(self, dbId, imgId, hashes):
        return imgdb.addKeywordsImg(dbId, imgId, hashes)

    @utils.require_known_db_id
    def query_img_blob(self, dbId, data, numres, sketch=0, fast=False):
        dbSpace = self.db_spaces[dbId]

        # return [[resId,resRatio]]
        # update internal counters
        numres = int(numres) + 1
        count_query(dbSpace)
        # do query
        results = imgdb.queryImgBlob(dbId, data, numres, sketch, fast)

        res = self._normalize_results(results)

        logger.debug("queryImgBlob() ret=" + str(res))
        return res

    @utils.require_known_db_id
    @utils.dump_args
    def query_img_path(self, dbId, path, numres, sketch=0, fast=False):
        dbSpace = self.db_spaces[dbId]

        # return [[resId,resRatio]]
        # update internal counters
        numres = int(numres) + 1
        count_query(dbSpace)
        # do query
        results = imgdb.queryImgPath(dbId, path, numres, sketch, fast)

        res = self._normalize_results(results)

        logger.debug("queryImgPath() ret=" + str(res))
        return res

    @utils.require_known_db_id
    @utils.dump_args
    def query_img_id(self, db_id: int, image_id: int, numres: int, sketch=0, fast: bool = False) -> Iterable:
        db_space = self.db_spaces[db_id]

        # return [[resId,resRatio]]

        # update internal counters
        numres = int(numres) + 1
        count_query(db_space)

        # do query
        results = imgdb.queryImgID(db_id, image_id, numres, sketch, fast)

        res = self._normalize_results(results)

        logger.debug("queryImgID() ret=" + str(res))
        return res

    def _pairgen(self, results: tuple) -> Iterable:
        results_iter = reversed(results)
        for rsc in results_iter:
            rid = next(results_iter, 0)
            yield rid, self._norm_rsc(rsc)

    def _norm_rsc(self, rsc):
        rsc = -100.0 * rsc / 38.70  # normalize # TODO is this normalization factor still valid?

        # sanity checks
        if rsc < 0:
            rsc = 0.0

        if rsc > 100:
            rsc = 100.0
        return rsc

    def _normalize_results(self, results: tuple) -> Iterable:
        """Normalize results returned by imgdb """
        res = self._pairgen(results)
        return res
