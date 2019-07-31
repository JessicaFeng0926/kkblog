from django.urls import re_path
from . import views

urlpatterns=[
    #这是处理点赞和取消点赞的路由
    re_path(r'^thumbup/$',views.ThumbupView.as_view(),name='thumbup'),
    #下面是处理关注和取消关注的路由
    re_path(r'^follow/$',views.FollowView.as_view(),name='follow'),
]