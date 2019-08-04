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
    
    send_title=''
    send_body=''
    #第二步，根据发送类型发送邮件

    if send_type==1:
        send_title='欢迎注册kkblog'
        send_body='请点击下面的链接完成账号激活:\n'+'http://127.0.0.1:8000/users/user_activate/'+code+'\n注意：链接有效时长为5分钟，激活完成会自动跳转到登录页面。'
        send_mail(send_title,send_body,EMAIL_FROM,[email])
    
    if send_type==2:
        send_title='kkblog重置密码'
        send_body='请点击下面的链接重置密码：\n'+'http://127.0.0.1:8000/users/reset/'+code+'\n注意：链接有效时长为5分钟，重置完成会自动跳转到登录页面。'
        send_mail(send_title,send_body,EMAIL_FROM,[email])

    if send_type==3:
        send_title='kkblog修改邮箱'
        send_body='您此次修改邮箱的验证码是:\n'+code+'\n注意，验证码的有效时长是5分钟，验证完成会跳转到登录页面。'
        send_mail(send_title,send_body,EMAIL_FROM,[email])



