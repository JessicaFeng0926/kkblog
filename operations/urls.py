from django.urls import re_path
from . import views

urlpatterns=[
    #这是处理点赞和取消点赞的路由
    re_path(r'^thumbup/$',views.ThumbupView.as_view(),name='thumbup'),
    #下面是处理关注和取消关注的路由
    re_path(r'^follow/$',views.FollowView.as_view(),name='follow'),
    #下面是收藏和取消收藏功能的路由
    re_path(r'^collect/$',views.CollectView.as_view(),name='collect'),
    #下面是用户移动收藏博客的路由
    re_path(r'^move/(\d+)/$',views.MoveView.as_view(),name='move'),
    #下面是用户把消息标位已读的路由
    re_path(r'^read/$',views.ReadView.as_view(),name='read'),
    #下面是用户删除消息的路由
    re_path(r'^delete_msg/$',views.DeleteMsgView.as_view(),name='delete_msg'),
    #下面是用户评论的路由
    re_path(r'^comment/$',views.CommentView.as_view(),name='comment'),
    #下面是博主删除评论的路由
    re_path(r'^delete_comment/$',views.DeleteCommentView.as_view(),name='delete_comment'),
]