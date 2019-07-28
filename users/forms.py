from django import forms
from captcha.fields import CaptchaField


class UserRegisterForm(forms.Form):
    '''这是用户注册的表单类'''
    email=forms.EmailField(required=True)
    password=forms.CharField(required=True,min_length=3,max_length=15,
    error_messages={
        'required':'密码必须填写',
        'min_length':'密码不能少于3位',
        'max_length':'密码不能多于15位',
    })
    password1=forms.CharField(required=True,min_length=3,max_length=15,
    error_messages={
        'required':'密码必须填写',
        'min_length':'密码不能少于3位',
        'max_length':'密码不能多于15位',
    })

    #下面是验证码
    captcha=CaptchaField()

class UserLoginForm(forms.Form):
    '''这是用户登录的表单类'''
    email=forms.EmailField(required=True)
    password=forms.CharField(required=True,min_length=3,max_length=15,
    error_messages={
        'required':'密码必须填写',
        'min_length':'密码不能少于3位',
        'max_length':'密码不能多于15位',
    })
