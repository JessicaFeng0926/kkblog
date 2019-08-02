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
]