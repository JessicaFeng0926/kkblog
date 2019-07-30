from . import views
from django.urls import re_path

urlpatterns=[
    re_path(r'^delete_topic/$',views.DeleteTopicView.as_view(),name='delete_topic'),
    re_path(r'^delete_blog/$',views.DeleteBlogView.as_view(),name='delete_blog'),
]