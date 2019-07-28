from django.core.mail import send_mail
import random
from users.models import EmailVerifyCode
from kkblog.settings import EMAIL_FROM

def get_random_code(code_length):
    '''这是生成随机验证码的函数'''
    code=''
    code_source='1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    for i in range(code_length):
        code+=random.choice(code_source)
    return code

def send_email_code(email,send_type):
    '''这是根据发送类型发送邮件的函数'''
    #第一步，创建验证码，存进数据库，用于比对
    code=get_random_code(8)
    evc=EmailVerifyCode()
    evc.code=code
    evc.email=email
    evc.send_type=send_type
    evc.save()

    #第二步，根据发送类型发送邮件

    if send_type==1:
        send_title='欢迎注册kkblog'
        send_body='请点击下面的链接完成账号激活:\n'+'http://127.0.0.1:8000/users/user_activate/'+code
        send_mail(send_title,send_body,EMAIL_FROM,[email])
    



