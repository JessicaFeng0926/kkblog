import xadmin
from . models import EmailVerifyCode

class EmailVerifyCodeXadmin(object):
    '''这是邮箱验证码表的管理类'''
    list_display=['code','email','send_type','addtime']



#注册
xadmin.site.register(EmailVerifyCode,EmailVerifyCodeXadmin)