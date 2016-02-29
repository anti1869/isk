"""
Urls configuration for REST endpoint.
"""

from isk.web.rest.views import db, images
from isk.web.rest.views.generic import NotImplementedView

urlconf = (

    # API mainpage
    ("GET", "/", NotImplementedView),

    # Database management
    ("GET", "/db/", db.DBListView),
    ("POST", "/db/", db.DBListView),
    ("GET", "/db/{db_id}/", db.DBView),
    ("DELETE", "/db/{db_id}/", db.DBView),
    ("POST", "/db/{db_id}/reset/", NotImplementedView),

    # Images management
    ("GET", "/db/{db_id}/images/", images.ImagesListView),
    ("POST", "/db/{db_id}/images/", NotImplementedView),
    ("GET", "/db/{db_id}/images/{image_id}/", images.ImageView),
    ("DELETE", "/db/{db_id}/images/{image_id}/", NotImplementedView),
    ("GET", "/db/{db_id}/images/{image_id}/keywords/", images.ImageKeywordsView),
    ("POST", "/db/{db_id}/images/{image_id}/keywords/", NotImplementedView),
    ("DELETE", "/db/{db_id}/images/{image_id}/keywords/", NotImplementedView),

    # Querying
    ("GET", "/db/{db_id}/query/", NotImplementedView),

    # Keywords management
    ("GET", "/db/{db_id}/keywords/", NotImplementedView),
    ("POST", "/db/{db_id}/keywords/", NotImplementedView),
    ("GET", "/db/{db_id}/keywords/{keyword_id}/", NotImplementedView),
    ("DELETE", "/db/{db_id}/keywords/{keyword_id}/", NotImplementedView),
)
