import xadmin
from .models import Blog,Topic,CollectBookMark

class TopicXadmin(object):
    '''这是主题的管理类'''
    list_display=['owner','topic_name','is_default','is_delete','addtime']

class BlogXadmin(object):
    '''这是博客的管理类'''
    list_display=['author','blog_title','category','blog_topic','is_delete','click_num','thumb_num','comment_num','addtime']

class CollectBookMarkXadmin(object):
    '''这是收藏夹的管理类'''
    list_display=['owner','bookmark_name','is_default','is_delete','addtime']

#注册
xadmin.site.register(Topic,TopicXadmin)
xadmin.site.register(Blog,BlogXadmin)
xadmin.site.register(CollectBookMark,CollectBookMarkXadmin)
