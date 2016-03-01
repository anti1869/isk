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

from sunhead.conf import settings

from isk.backends.factory import backend
from isk.urldownloader import url_to_file

logger = logging.getLogger(__name__)

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'  # Whether this module is imported by readthedocs.org builder
if not on_rtd:  # If so, disable loading any extension modules RTC can't hadle
    # TODO: Check rtd stuff here
    pass


# Globals
daemon_start_time = time.time()
has_shutdown = False


def query_img_id(db_id: int, image_id: int, numres: int = 12, sketch: bool = False, fast: bool = False) -> tuple:
    """
    Return the most similar images to the supplied one.
    The supplied image must be already indexed, and is referenced by its ID.

    :param db_id: Database space id.
    :param image_id: Target image id.
    :param numres: Number of results to return. The target image is on the result list.
    :param sketch: False for photographs, True for hand-sketched images or low-resolution vector images.
    :param fast: if true, only the average color for each image is considered.
        Image geometry/features are ignored. Search is faster this way.
    :since: 0.7
    :change: 0.9.3: added parameter 'sketch'
    :return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
        (id is Integer, score is Double)
    """    

    # TODO: Removed inefficicent balancer from here. Implement better one

    results = backend.query_img_id(db_id, image_id, numres, sketch, fast)
    result_tuple = tuple(results)
    return result_tuple



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
    
    return backend.query_img_blob(dbId, data.data, numres, sketch, fast)


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
    
    return backend.query_img_path(dbId, path, numres, sketch, fast)


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
        res = backend.add_image_blob(dbId, data.data, id)
    except Exception as e:
        if str(e) == 'image already in db':
            logger.warn(e)
        else:
            logger.error(e)
        return res
    
    return res


def add_img(db_id: int, image_id: int, filename: str, file_is_url: bool = False) -> bool:
    """
    Add image to database space. Image file is read, processed and indexed.
    After this indexing is done, image can be removed from file system.

    :param db_id: Database space id.
    :param image_id: Target image id. The image located on filename will be indexed and from now on should be
        refered to isk-daemon as this supplied id.
    :param filename: Physical full file path for the image to be indexed.
        Should be in one of the supported formats
        ('jpeg', 'jpg', 'gif', 'png', 'rgb', 'pbm', 'pgm', 'ppm', 'tiff', 'tif', 'rast', 'xbm', 'bmp').
        For better results image should have dimension of at least 128x128. Thumbnails are ok.
        Bigger images will be scaled down to 128x128.
    :param file_is_url: if true, filename is interpreted as an HTTP url and the remote image
        it points to downloaded and saved to a temporary location (same directory where database file is)
        before being added to database.
    
    :since: 0.7
    :return:  True in case of success.
    """
    if file_is_url: # download it first
        # TODO: May be this need to be deprecated
        tempFName = os.path.expanduser(settings.core.get('database','databasePath')) + ('_tmp_%d_%d.jpg' % (db_id, image_id))
        url_to_file(filename, tempFName)
        filename = tempFName

    res = False

    try:
        # TODO id should be unsigned long int or something even bigger, also must review swig declarations
        res = backend.add_image(db_id, filename, image_id)
    except Exception as e:
        if str(e) == 'image already in db':
            logger.warn(e)
        else:
            logger.error(e)
        return res
    
    if (file_is_url):
        os.remove(filename)
    
    return res


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
    return backend.remove_img(dbId, id)


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
    return backend.is_image_on_db(dbId, id)


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
    return backend.get_image_dimensions(dbId, id)


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
    return backend.calc_avgl_diff(dbId, id1, id2)


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
    
    return backend.calc_diff(dbId, id1, id2)


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
    return backend.get_image_avgl(dbId, id1)


def get_db_img_id_list(db_id: int) -> tuple:
    """
    Return list of image ids on database space.

    :since: 0.7
    :param db_id: Database space id.
    :return:  array of image ids
    """    

    result = backend.get_img_id_list(db_id)
    return result


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
    return backend.add_keyword_img(dbId, imgId, hash)


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
    return backend.getIdsBloomFilter(dbId)


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
    return backend.get_cluster_keywords(dbId, numClusters, keywords)


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
    return backend.get_cluster_db(dbId, numClusters)


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
    return backend.get_keywords_popular(dbId, numres)


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
    return backend.get_keywords_visual_distance(dbId, distanceType, keywords)


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
    
    return backend.get_all_imgs_by_keywords(dbId, numres, kwJoinType, keywordIds)


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
    return backend.query_img_id_fast_keywords(dbId, imgId, numres, kwJoinType, keywords)


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
    return backend.query_img_id_keywords(dbId, imgId, numres, kwJoinType, keywordIds)


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
    
    return backend.most_popular_keywords(dbId, imgs, excludedKwds, count, mode)


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
    return backend.get_keywords_img(dbId, imgId)


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
    return backend.remove_all_keywords_img(dbId, imgId)


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
    return backend.remove_keyword_img(dbId, imgId, hash)


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
    return backend.add_keywords_img(dbId, imgId, hashes)


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
    return backend.add_dir(dbId, path, recurse, fname_as_id)


exporting = (
    query_img_id,
    add_img,
    remove_img,
    remove_img_bulk,
    is_img_on_db,
    get_img_dimensions,
    calc_img_avgl_diff,
    calc_img_diff,
    get_img_avgl,
    get_db_img_id_list,
    add_dir,
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
    get_ids_bloom_filter,
    most_popular_keywords,
    query_img_blob,
    query_img_path,
    add_img_blob,

    get_cluster_db,
    get_cluster_keywords,
)
