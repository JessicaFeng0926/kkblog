import xadmin
from .models import UserComment

class UserCommentXadmin(object):
    '''这是用户评论的管理类'''
    list_display=['speaker','listener_id','listener_read','author_read']


#注册
xadmin.site.register(UserComment,UserCommentXadmin)