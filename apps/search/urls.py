from tornado.web import url
from apps.search.handler import BreedHandler,BreedDetailHandler,BreedCommentHandler,CommentReplyHandler,CommentsLikeHandler

urlpattern = (
    url("/breeds/", BreedHandler),
    url("/breeds/([0-9]+)/",BreedDetailHandler),

    url("/breeds/([0-9]+)/comments/",BreedCommentHandler),
    url("/comments/([0-9]+)/replys/",CommentReplyHandler),

    url("/comments/([0-9]+)/likes/",CommentsLikeHandler),
)