from django.urls import re_path
from . import views

urlpatterns=[
    #登录
    re_path(r'^login/$',views.UserLoginView.as_view(),name='login'),
    #注册
    re_path(r'^register/$',views.UserRegisterView.as_view(),name='register'),
    #退出
    re_path(r'^logout/$',views.UserLogoutView.as_view(),name='logout'),
    #激活
    re_path(r'^user_activate/(\w+)/$',views.UserActivateView.as_view(),name='user_activate'),
    #忘记密码
    re_path(r'^forget/$',views.UserForgetView.as_view(),name='forget'),
    #重置密码
    re_path(r'^reset/(\w+)$',views.UserResetView.as_view(),name='reset'),
    #个人中心首页
    re_path(r'^personal_center/$',views.UserPersonalCenterView.as_view(),name='pc'),
    #我的博客
    re_path(r'^myblogs/$',views.MyblogsView.as_view(),name='myblogs'),
    #我的博客详情
    re_path(r'^myblog_detail/(\d+)/$',views.MyBlogDetailView.as_view(),name='myblog_detail'),
]