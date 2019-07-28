from django.urls import re_path
from . import views

urlpatterns=[
    re_path(r'^login/$',views.UserLoginView.as_view(),name='login'),
    re_path(r'^register/$',views.UserRegisterView.as_view(),name='register'),
    re_path(r'^logout/$',views.UserLogoutView.as_view(),name='logout'),
    re_path(r'^user_activate/(\w+)/$',views.UserActivateView.as_view(),name='user_activate'),
]