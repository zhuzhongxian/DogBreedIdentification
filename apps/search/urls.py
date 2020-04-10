from tornado.web import url
from apps.search.handler import BreedHandler,BreedDetailHandler,BreedCommentHandler,CommentReplyHandler,CommentsLikeHandler,BreedFollowHandler,SearchHandler

urlpattern = (
    url("/search/", SearchHandler),

    url("/breeds/", BreedHandler),
    url("/breeds/([0-9]+)/",BreedDetailHandler),

    url("/breeds/([0-9]+)/comments/",BreedCommentHandler),
    url("/breeds/([0-9]+)/follow/",BreedFollowHandler),
    url("/comments/([0-9]+)/replys/",CommentReplyHandler),

    url("/comments/([0-9]+)/likes/",CommentsLikeHandler),


)