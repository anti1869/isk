"""
Urls configuration for REST endpoint.
"""

from isk.web.rest.views import db, images, query, dropbox, keywords
from isk.web.rest.views.generic import NotImplementedView

urlconf = (

    # API mainpage
    ("GET", "/", NotImplementedView),

    # Database management
    ("GET", "/db/", db.DBListView),
    ("POST", "/db/", db.DBListView),
    ("GET", "/db/{db_id}/", db.DBView),
    ("DELETE", "/db/{db_id}/", db.DBView),
    ("POST", "/db/{db_id}/reset/", db.DBResetView),

    # Images management
    ("GET", "/db/{db_id}/images/", images.ImagesListView),
    ("GET", "/db/{db_id}/images/{image_id}/", images.ImageView),
    ("DELETE", "/db/{db_id}/images/{image_id}/", images.ImageView),
    ("GET", "/db/{db_id}/images/{image_id}/keywords/", images.ImageKeywordsView),
    ("POST", "/db/{db_id}/images/{image_id}/keywords/", images.ImageKeywordsView),
    ("DELETE", "/db/{db_id}/images/{image_id}/keywords/", images.ImageKeywordsView),

    # Adding images to DB
    ("GET", "/db/{db_id}/dropbox/", NotImplementedView),
    ("POST", "/db/{db_id}/dropbox/url/", dropbox.ImagesDropboxUrl),
    ("POST", "/db/{db_id}/dropbox/image/", dropbox.ImagesDropboxFile),
    ("POST", "/db/{db_id}/dropbox/archive/", dropbox.ImagesDropboxArchive),

    # Querying
    ("GET", "/db/{db_id}/query/", query.SimilarImagesQuery),
    ("POST", "/db/{db_id}/query/", NotImplementedView),

    # Keywords management
    ("GET", "/db/{db_id}/keywords/", keywords.KeywordsListView),
    ("GET", "/db/{db_id}/keywords/{keyword_id}/", keywords.ImagesByKeyword),
)
