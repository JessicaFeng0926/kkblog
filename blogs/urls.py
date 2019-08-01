from . import views
from django.urls import re_path

urlpatterns=[
    re_path(r'^delete_topic/$',views.DeleteTopicView.as_view(),name='delete_topic'),
    re_path(r'^delete_blog/$',views.DeleteBlogView.as_view(),name='delete_blog'),
    #下面是某位博主的所有博客列表页路由
    re_path(r'^blog_list/(\d+)/$',views.BlogListView.as_view(),name='blog_list'),
    #下面是某位博主的某篇博客详情页路由
    re_path(r'^blog_detail/(\d+)/$',views.BlogDetailView.as_view(),name='blog_detail'),
    #下面是删除收藏夹的路由
    re_path(r'^delete_bookmark/$',views.DeleteBookmarkView.as_view(),name='delete_bookmark')
    
]