###############################################################################
# begin                : Sun Jan  8 21:24:38 BRST 2012
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

# Undocumented members declaration moved to /docs/api.rst
# Now using Sphinx as autodoc builder for Read The Docs (as it's most popular at the moment).
# See http://sphinx-doc.org and https://readthedocs.org

import time
import logging
import os

import statistics
from isk.urldownloader import urlToFile
from isk import settings, __version__

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'  # Whether this module is imported by readthedocs.org builder
if not on_rtd:  # If so, disable loading any extension modules RTC can't hadle
    from isk.imgseeklib.imagedb import ImgDB

# Globals
daemon_start_time = time.time()
has_shutdown = False
isk_version = __version__
db_path = os.path.expanduser(settings.core.get('database', 'databasePath'))

# misc daemon inits
logger = logging.getLogger(__name__)
logger.info('+- Initializing isk api (version %s) ...' % isk_version)
if not on_rtd:  # Again, disable this for RTD builder. All it needs are only docstrings.
    img_db = ImgDB(settings)
    img_db.loadalldbs(db_path)

logger.info('| image database initialized')


# Common functions for all comm backends
def query_img_id(db_id, id, numres=12, sketch=0, fast=False):
    """
    Return the most similar images to the supplied one.
    The supplied image must be already indexed, and is referenced by its ID.

    :type  db_id: number
    :param db_id: Database space id.
    :type  id: number
    :param id: Target image id.
    :type  numres: number
    :param numres: Number of results to return. The target image is on the result list.
    :type  sketch: number
    :param sketch: 0 for photographs, 1 for hand-sketched images or low-resolution vector images.
    :type fast: boolean
    :param fast: if true, only the average color for each image is considered.
        Image geometry/features are ignored. Search is faster this way.
    :rtype:   array
    :since: 0.7
    :change: 0.9.3: added parameter 'sketch'
    :return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
        (id is Integer, score is Double)
    """    
    db_id = int(db_id)
    id = int(id)
    numres = int(numres)

    # TODO: Removed inefficicent balancer from here. Implement better one

    return img_db.query_img_id(db_id, id, numres, sketch, fast)


def query_img_blob(dbId, data, numres=12, sketch=0, fast=False):
    """
    Return the most similar images to the supplied one.
    The target image is specified by its raw binary file data.
    Most common formats are supported.

    :type  dbId: number
    :param dbId: Database space id.
    :type  data: binary data
    :param data: Target image file binary data.
    :type  numres: number
    :param numres: Number of results to return. The target image is on the result list.
    :type  sketch: number
    :param sketch: 0 for photographs, 1 for hand-sketched images or low-resolution vector images. 
    :type fast: boolean
    :param fast: if true, only the average color for each image is considered. Image geometry/features are ignored.
        Search is faster this way.
    :rtype:   array
    
    :since: 0.9.3
    :return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
        (id is Integer, score is Double)
    """    
    dbId = int(dbId)
    numres = int(numres)
    
    return img_db.query_img_blob(dbId, data.data, numres, sketch, fast)


def query_img_path(dbId, path, numres=12, sketch=0, fast=False):
    """
    Return the most similar images to the supplied one.
    The target image is specified using it's full path on the server filesystem.

    :type  dbId: number
    :param dbId: Database space id.
    :type  path: string
    :param path: Target image pth on the server disk.
    :type  numres: number
    :param numres: Number of results to return. The target image is on the result list.
    :type  sketch: number
    :param sketch: 0 for photographs, 1 for hand-sketched images or low-resolution vector images. 
    :type fast: boolean
    :param fast: if true, only the average color for each image is considered. Image geometry/features are ignored.
        Search is faster this way.
    :rtype:   array
    
    :since: 0.9.3
    :return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
        (id is Integer, score is Double)
    """    
    dbId = int(dbId)
    numres = int(numres)
    
    return img_db.query_img_path(dbId, path, numres, sketch, fast)


def add_img_blob(dbId, id, data):
    """
    Add image to database space. Image data is passed directly. It is then processed and indexed. 

    :type  dbId: number
    :param dbId: Database space id.
    :type  id: number
    :param id: Target image id. The image located on filename will be indexed and from now on should be refered
        to isk-daemon as this supplied id.
    :type  data: binary 
    :param data: Image binary data
    :rtype:   number
    
    :since: 0.9.3
    :return:  1 in case of success.
    """
    dbId = int(dbId)
    id = int(id)

    try:
        # TODO id should be unsigned long int or something even bigger, also must review swig declarations
        res = img_db.add_image_blob(dbId, data.data, id)
    except Exception as e:
        if str(e) == 'image already in db':
            logger.warn(e)
        else:
            logger.error(e)
        return res
    
    return res


def add_img(dbId, id, filename, fileIsUrl=False):
    """
    Add image to database space. Image file is read, processed and indexed.
    After this indexing is done, image can be removed from file system.

    :type  dbId: number
    :param dbId: Database space id.
    :type  id: number
    :param id: Target image id. The image located on filename will be indexed and from now on should be
        refered to isk-daemon as this supplied id.
    :type  filename: string
    :param filename: Physical full file path for the image to be indexed.
        Should be in one of the supported formats
        ('jpeg', 'jpg', 'gif', 'png', 'rgb', 'pbm', 'pgm', 'ppm', 'tiff', 'tif', 'rast', 'xbm', 'bmp').
        For better results image should have dimension of at least 128x128. Thumbnails are ok.
        Bigger images will be scaled down to 128x128.
    :type  fileIsUrl: boolean
    :param fileIsUrl: if true, filename is interpreted as an HTTP url and the remote image
        it points to downloaded and saved to a temporary location (same directory where database file is)
        before being added to database.
    :rtype:   number
    
    :since: 0.7
    :return:  1 in case of success.
    """
    dbId = int(dbId)
    id = int(id)

    if fileIsUrl: # download it first
        tempFName = os.path.expanduser(settings.core.get('database','databasePath')) + ('_tmp_%d_%d.jpg' % (dbId,id))
        urlToFile(filename,tempFName)
        filename = tempFName
    res = 0
    try:
        #TODO id should be unsigned long int or something even bigger, also must review swig declarations
        res = img_db.add_image(dbId, filename, id)
    except Exception as e:
        if str(e) == 'image already in db':
            logger.warn(e)
        else:
            logger.error(e)
        return res
    
    if (fileIsUrl): os.remove(filename)    
    
    return res


def save_db(dbId):
    """
    Save the supplied database space if the it has already been saved with a filename (previous call to L{saveDbAs}).
    B{NOTE}: This operation should be used for exporting single database spaces.
    For regular server instance database persistance, use L{saveAllDbs} and L{loadAllDbs}.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   number
    
    :since: 0.7
    :return:  1 in case of success.
    """        
    dbId = int(dbId)
    return img_db.savedb(dbId)


def save_db_as(dbId, filename):
    """
    Save the supplied database space if the it has already been saved with a filename
    (subsequent save calls can be made to L{saveDb}).

    :type  dbId: number
    :param dbId: Database space id.
    :type  filename: string
    :param filename: Target filesystem full path of the file where data should be stored at.
        B{NOTE}: This data file contains a single database space and should be used for import/export purposes only.
        Do not try to load it with a call to L{loadAllDbs}.
    :rtype:   number
    
    :since: 0.7
    :return:  1 in case of success.
    """
    dbId = int(dbId)
    return img_db.savedbas(dbId, filename)


def load_db(dbId, filename):
    """
    Load the supplied single-database-space-dump into a database space of given id.
    An existing database space with the given id will be completely replaced.

    :type  dbId: number
    :param dbId: Database space id.
    :type  filename: string
    :param filename: Target filesystem full path of the file where data is stored at.
        B{NOTE}: This data file contains a single database space and should be used for import/export purposes only.
        Do not try to load it with a call to L{loadAllDbs} and vice versa.
    :rtype:   number
    
    :since: 0.7
    :return:  dbId in case of success.
    """    
    dbId = int(dbId)    
    return img_db.loaddb(dbId, filename)


def remove_img(dbId, id):
    """
    Remove image from database space.

    :type  dbId: number
    :param dbId: Database space id.
    :type  id: number
    :param id: Target image id.
    :rtype:   number
    
    :since: 0.7
    :return:  1 in case of success.
    """    
    id = int(id)
    dbId = int(dbId)    
    return img_db.remove_img(dbId, id)


def remove_img_bulk(dbId, ids):
    """
    Neat shortcut to remove whole bunch of images from database.

    :type  dbId: number
    :param dbId: Database space id.
    :type  id: list
    :param idList: List of image ids.

    :since: 0.10
    :return: True if all images was removed.
    """
    result = True
    for image_id in ids:
        result &= remove_img(dbId, image_id)
    return result


def reset_db(dbId):
    """
    Removes all images from a database space, frees memory, reset statistics.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   number
    
    :since: 0.7
    :return:  1 in case of success.
    """    
    dbId = int(dbId)    
    return img_db.resetdb(dbId)


def create_db(dbId):
    """
    Create new db space. Overwrite database space statistics if one with supplied id already exists.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   number
    
    :since: 0.7
    :return:  dbId in case of success
    """    
    dbId = int(dbId)
    return img_db.createdb(dbId)


def shutdown_server():
    """
    Request a shutdown of this server instance.

    :rtype:   number
    
    :since: 0.7
    :return:  always M{1}
    """
    global has_shutdown

    if has_shutdown: return 1 # already went through a shutdown
    
    if settings.core.getboolean('daemon','saveAllOnShutdown'):
            save_all_dbs()
            img_db.closedb()

    logger.info("Shuting instance down...")
    # from twisted.internet import reactor
    # reactor.callLater(1, reactor.stop)
    has_shutdown = True
    return 1


def get_db_img_count(dbId):
    """
    Return count of indexed images on database space.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   number
    
    :since: 0.7
    :return:  image count
    """    
    dbId = int(dbId)
    return img_db.get_img_count(dbId)


def is_img_on_db(dbId, id):
    """
    Return whether image id exists on database space.

    :type  dbId: number
    :param dbId: Database space id.
    :type  id: number
    :param id: Target image id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if image id exists
    """    
    dbId = int(dbId)
    id = int(id)
    return img_db.is_image_on_db(dbId, id)


def get_img_dimensions(dbId, id):
    """
    Returns image original dimensions when indexed into database.

    :type  dbId: number
    :param dbId: Database space id.
    :type  id: number
    :param id: Target image id.
    :rtype:   array
    
    :since: 0.7
    :return:  array in the form M{[width, height]}
    """    
    dbId = int(dbId)
    id = int(id)
    return img_db.get_image_dimensions(dbId, id)


def calc_img_avgl_diff(dbId, id1, id2):
    """
    Return average luminance (over three color channels) difference ratio

    :type  dbId: number
    :param dbId: Database space id.
    :type  id1: number
    :param id1: Target image 1 id.
    :type  id2: number
    :param id2: Target image 2 id.
    :rtype:   number
    
    :since: 0.7
    :return:  float representing difference. The smaller, the most similar.
    """    
    dbId = int(dbId)
    id1 = int(id1)
    id2 = int(id2)
    return img_db.calc_avgl_diff(dbId, id1, id2)


def calc_img_diff(dbId, id1, id2):
    """
    Return image similarity difference ratio. One value alone for an image pair doesn't mean much.
    These values should be compared pairwise against each other.
    
    The smaller the value between two images is (i.e. the more negative the value is),
    the more similar the 2 images are.

    Comparing one image against itself is a degenerate case and the value returned should be ignored.

    :type  dbId: number
    :param dbId: Database space id.
    :type  id1: number
    :param id1: Target image 1 id.
    :type  id2: number
    :param id2: Target image 2 id.
    :rtype:   number
    
    :since: 0.7
    :return:  float representing difference. The smaller, the most similar.
    """    
    dbId = int(dbId)
    id1 = int(id1)
    id2 = int(id2)
    
    return img_db.calc_diff(dbId, id1, id2)


def get_img_avgl(dbId, id):
    """
    Return image average color levels on the three color channels (YIQ color system)

    :type  dbId: number
    :param dbId: Database space id.
    :type  id: number
    :param id: Target image id.
    :rtype:   array of double
    
    :since: 0.7
    :return:  values for YIQ color channels
    """    
    dbId = int(dbId)
    id1 = int(id)
    return img_db.get_image_avgl(dbId, id1)


def get_db_list():
    """
    Return list defined database spaces.

    :rtype:   array
    
    :since: 0.7
    :return:  array of db space ids
    """    
    return img_db.get_db_list()


def get_db_img_id_list(dbId):
    """
    Return list of image ids on database space.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   array
    
    :since: 0.7
    :return:  array of image ids
    """    
    
    dbId = int(dbId)
    return img_db.get_img_id_list(dbId)


def get_db_detailed_list():
    """
    Return details for all database spaces.

    :rtype:   map
    
    :since: 0.7
    :return:  map key is database space id (as an integer), associated value is array with [getImgCount,
                            queryCount,
                            lastQueryPerMin,
                            queryMinCount,
                            queryMinCur,
                            lastAddPerMin,
                            addMinCount,
                            addMinCur,
                            addCount,
                            addSinceLastSave,
                            lastId,
                            lastSaveTime,
                            fileName
                            ]
    """    
    
    return img_db.get_db_detailed_list()


def save_all_dbs_as(path):
    """
    Persist all existing database spaces.

    :type  path: string
    :param path: Target filesystem full path of the file where data is stored at.
    :rtype:   number
    
    :since: 0.7
    :return:  total db spaces written
    """    
    
    return img_db.savealldbs(path)


def add_keyword_img(dbId, imgId, hash):
    """
    Adds a keyword to an image.

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgId: number
    :param imgId: Target image id.
    :type  hash: number
    :param hash: Keyword id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if operation was succesful
    """
    dbId = int(dbId)
    imgId = int(imgId)
    return img_db.add_keyword_img(dbId, imgId, hash)


def add_keyword_img_bulk(dbId, data):
    """
    Adds keywords to images in a bulk. You pass data as dict when keywords as keys and list of image id as values::

        {
            keyword1_id: [img1_id, img2_id],
            keyword2_id: [img1_id, img3_id],
            ...
        }

    This will save some network overhead.

    :param dbId: id of the image database to use.
    :param data: Keywords and list of image id in described format.
    :since: 0.10
    :return: True if all operations was successfull
    """

    result = True

    for keyword, id_list in data.items():

        # Convert keyword to int
        try:
            keyword_id = int(keyword)
        except ValueError:
            result &= False
            continue

        # Assign that keyword to images
        for img in id_list:
            try:
                img_id = int(img)
            except ValueError:
                result &= False
                continue

            result &= add_keyword_img(dbId, img_id, keyword_id)

    return bool(result)


def get_ids_bloom_filter(dbId):
    """
    Return bloom filter containing all images on given db id.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   bloom filter
    
    :since: 0.7
    :return:  bloom filter containing all images on given db id.
    """
    dbId = int(dbId)
    return img_db.getIdsBloomFilter(dbId)


def get_cluster_keywords(dbId, numClusters, keywords):
    """
    Return whether image id exists on database space.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if image id exists
    """    
    dbId = int(dbId)
    return img_db.get_cluster_keywords(dbId, numClusters, keywords)


def get_cluster_db(dbId, numClusters):
    """
    Return whether image id exists on database space.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if image id exists
    """    
    dbId = int(dbId)
    return img_db.get_cluster_db(dbId, numClusters)


def get_keywords_popular(dbId, numres):
    """
    Return whether image id exists on database space.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if image id exists
    """    
    dbId = int(dbId)
    return img_db.get_keywords_popular(dbId, numres)


def get_keywords_visual_distance(dbId, distanceType, keywords):
    """
    Return whether image id exists on database space.

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if image id exists
    """    
    dbId = int(dbId)
    return img_db.get_keywords_visual_distance(dbId, distanceType, keywords)


def get_all_imgs_by_keywords(dbId, numres, kwJoinType, keywords):
    """
    Return all images with the given keywords

    :type  dbId: number
    :param dbId: Database space id.
    :type  numres: number
    :param numres: Number of results desired
    :type  kwJoinType: number
    :param kwJoinType: Logical operator for target keywords: 1 for AND, 0 for OR
    :type  keywords: string
    :param keywords: comma separated list of keyword ids. An empty string will return random images.
    :rtype:   array

    :since: 0.7
    :return:  array of image ids
    """    
    dbId = int(dbId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    if len(keywordIds) == 0:
        keywordIds=[0]
    
    return img_db.get_all_imgs_by_keywords(dbId, numres, kwJoinType, keywordIds)


def query_img_id_fast_keywords(dbId, imgId, numres, kwJoinType, keywords):
    """
    Fast query (only considers average color) for similar images considering keywords

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgId: number
    :param imgId: Target image id. If '0', random images containing the target keywords will be returned.
    :type  numres: number
    :param numres: Number of results desired
    :type  kwJoinType: number
    :param kwJoinType: logical operator for keywords: 1 for AND, 0 for OR
    :type  keywords: string
    :param keywords: comma separated list of keyword ids.
    :rtype:   array
    
    :since: 0.7
    :return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
        (id is Integer, score is Double)
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    return img_db.query_img_id_fast_keywords(dbId, imgId, numres, kwJoinType, keywords)


def query_img_id_keywords(dbId, imgId, numres, kwJoinType, keywords):
    """
    Query for similar images considering keywords. The input keywords are used for narrowing the
    search space.

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgId: number
    :param imgId: Target image id. If '0', random images containing the target keywords will be returned.
    :type  numres: number
    :param numres: Number of results desired
    :type  kwJoinType: number
    :param kwJoinType: logical operator for keywords: 1 for AND, 0 for OR
    :type  keywords: string
    :param keywords: comma separated list of keyword ids. 
    :rtype:   array
    
    :since: 0.7
    :return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
        (id is Integer, score is Double)
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    return img_db.query_img_id_keywords(dbId, imgId, numres, kwJoinType, keywordIds)


def query_img_id_keywords_bulk(dbId, imgKwList, numres, kwJoinType):
    """
    Shortcut for querying for similar images considering keywords in bulk. You pass list of tuples::

        [
            (img1_id, 'kw1_id,kw2_id'),
            (img2_id, 'kw3_id'),
            ...
        ]

    In return you get list of results::

        [
            (img1_id, [(img2_id, img2_score), (img5_id, img5_score), ...]),
            (img2_id, [(img16_id, img16_score), ...]),
        ]

    This will save you some network overhead over calling queryImgIDKeywords one-by-one.

    :type  dbId: number
    :param dbId: Database space id
    :type imgKwList: tuple
    :param imgKwList: List of queries in described format. Keywords is a comma-separated list of keyword ids.
    :type  numres: number
    :param numres: Number of results desired
    :type  kwJoinType: number
    :param kwJoinType: logical operator for keywords: 1 for AND, 0 for OR
    :since: 0.10
    :return: List of image ids and corresponding results in format, described above.
    """

    total_results = []
    for image_id, keywords in imgKwList:
        query_result = query_img_id_keywords(dbId, image_id, numres, kwJoinType, keywords)
        total_results.append((image_id, query_result))

    return total_results


def most_popular_keywords(dbId, imgs, excludedKwds, count, mode):
    """
    Returns the most frequent keywords associated with a given set of images 

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgs: string
    :param imgs: Comma separated list of target image ids
    :type  excludedKwds: string
    :param excludedKwds: Comma separated list of keywords ids to be excluded from the frequency count
    :type  count: number
    :param count: Number of keyword results desired
    :type  mode: number
    :param mode: ignored, will be used on future versions.
    :rtype:   array
    
    :since: 0.7
    :return:  array of keyword ids and frequencies: [kwd1_id, kwd1_freq, kwd2_id, kwd2_freq, ...]
    """    
    dbId = int(dbId)
    excludedKwds = [int(x) for x in excludedKwds.split(',') if len(x) > 0]
    imgs = [int(x) for x in imgs.split(',') if len(x) > 0]
    
    return img_db.most_popular_keywords(dbId, imgs, excludedKwds, count, mode)


def get_keywords_img(dbId, imgId):
    """
    Returns all keywords currently associated with an image.

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgId: number
    :param imgId: Target image id.
    :rtype:   array
    
    :since: 0.7
    :return:  array of keyword ids
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return img_db.get_keywords_img(dbId, imgId)


def remove_all_keyword_img(dbId, imgId):
    """
    Remove all keyword associations this image has.
    
    Known issue: keyword based queries will continue to consider the image to be associated
    to this keyword until the database is saved and restored.

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgId: number
    :param imgId: Target image id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if operation succeeded
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return img_db.remove_all_keywords_img(dbId, imgId)


def remove_all_keyword_img_bulk(dbId, imgIdList):
    """
    Remove all keyword associations for all images in list.

    This is just convenience shortcut for removeAllKeywordImg being called in loop.
    Saves network overhead, though.

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgIdList: list
    :param imgIdList: List of target image id.
    :rtype:   boolean

    :since: 0.10
    :return:  True if all calls succeeded
    """
    result = True
    for img_id in imgIdList:
        result &= remove_all_keyword_img(dbId, img_id)

    return result


def remove_keyword_img(dbId, imgId, hash):
    """
    Remove the association of a keyword to an image
    
    Known issue: keyword based queries will continue to consider the image to be associated to this
    keyword until the database is saved and restored.

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgId: number
    :param imgId: Target image id.
    :type  hash: number
    :param hash: Keyword id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if operation succeeded
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return img_db.remove_keyword_img(dbId, imgId, hash)


def add_keywords_img(dbId, imgId, hashes):
    """
    Associate keywords to image

    :type  dbId: number
    :param dbId: Database space id.
    :type  imgId: number
    :param imgId: Target image id.
    :type  hashes: list of number
    :param hashes: Keyword hashes to associate
    :rtype:   boolean
    
    :since: 0.7
    :return:  true if image id exists
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return img_db.add_keywords_img(dbId, imgId, hashes)


def add_dir(dbId, path, recurse, fname_as_id=False):
    """
    Visits a directory recursively and add supported images into database space.

    :type  dbId: number
    :param dbId: Database space id.
    :type  path: string
    :param path: Target filesystem full path of the initial dir.
    :type  recurse: number
    :param recurse: 1 if should visit recursively
    :type fname_as_id: bool
    :param fname_as_id: Whether to use file names as id. If false, id will be assigned automatically.
    :rtype:   number
    
    :since: 0.7
    :return:  count of images succesfully added
    """    
    
    dbId = int(dbId)
    return img_db.add_dir(dbId, path, recurse, fname_as_id)


def load_all_dbs_as(path):
    """
    Loads from disk all previously persisted database spaces. (File resulting from a previous call to L{saveAllDbs}).

    :type  path: string
    :param path: Target filesystem full path of the file where data is stored at.
    :rtype:   number
    
    :since: 0.7
    :return:  total db spaces read
    """    
    
    return img_db.loadalldbs(path)


def save_all_dbs():
    """
    Persist all existing database spaces on the data file defined at the config file I{settings.py}

    :rtype:   number
    
    :since: 0.7
    :return:  count of persisted db spaces
    """
    
    return img_db.savealldbs(settings.core.get('database', 'databasePath'))


def load_all_dbs():
    """
    Loads from disk all previously persisted database spaces on the data file defined at the config file I{settings.py}

    :rtype:   number
    
    :since: 0.7
    :return:  count of persisted db spaces
    """    
    
    return img_db.loadalldbs(settings.core.get('database', 'databasePath'))


def remove_db(dbid):
    """
    Remove a database. All images associated with it are also removed.

    :rtype:   boolean
    
    :since: 0.7
    :return:  true if succesful
    """    
    
    return img_db.remove_db(dbid)


def get_global_server_stats():
    """
    Return the most similar images to the supplied one.

    :rtype:   map
    
    :since: 0.7
    :return:  key is stat name, value is value.
        Keys are ['isk-daemon uptime', 'Number of databases', 'Total memory usage', 'Resident memory usage',
        'Stack memory usage']
    """    
    
    stats = {}
    
    stats['isk-daemon uptime'] = statistics.human_readable(time.time() - daemon_start_time)
    stats['Number of databases'] = len(img_db.get_db_list())
    stats['Total memory usage'] = statistics.memory()
    stats['Resident memory usage'] = statistics.resident()
    stats['Stack memory usage'] = statistics.stacksize()    
    
    return stats


def is_valid_db(dbId):
    """
    Return whether database space id has already been defined

    :type  dbId: number
    :param dbId: Database space id.
    :rtype:   boolean
    
    :since: 0.7
    :return:  True if exists
    """    
    
    dbId = int(dbId)
    return img_db.is_valid_db(dbId)


def get_isk_log(window = 30):
    """
    Returns the last lines of text in the iskdaemon instance log

    :type  window: number
    :param window: number of lines to retrieve 

    :rtype:   string
    :return:  text block
    :since: 0.9.3
    """
    from isk.utils import tail
    
    return tail(open(settings.core.get('daemon','logPath')), window)

public = [
     query_img_id,
     add_img,
     save_db,
     load_db,
     remove_img,
     remove_img_bulk,
     reset_db,
     remove_db,
     create_db,
     get_db_img_count,
     is_img_on_db,
     get_img_dimensions,
     calc_img_avgl_diff,
     calc_img_diff,
     get_img_avgl,
     get_db_list,
     get_db_detailed_list,
     get_db_img_id_list,
     is_valid_db,
     get_global_server_stats,
     save_db_as,
     save_all_dbs,
     load_all_dbs,
     save_all_dbs_as,
     load_all_dbs_as,
     add_dir,
     shutdown_server,
     add_keyword_img,
     add_keywords_img,
     add_keyword_img_bulk,
     remove_keyword_img,
     remove_all_keyword_img,
     remove_all_keyword_img_bulk,
     get_keywords_img,
     query_img_id_keywords,
     query_img_id_keywords_bulk,
     query_img_id_fast_keywords,
     get_all_imgs_by_keywords,
     get_keywords_visual_distance,
     get_keywords_popular,
     get_cluster_db,
     get_cluster_keywords,
     get_ids_bloom_filter,
     most_popular_keywords,
     get_isk_log,
     query_img_blob,
     query_img_path,
     add_img_blob,
]
