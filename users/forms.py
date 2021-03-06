from django import forms
from captcha.fields import CaptchaField
from users.models import UserProfile
import re


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

class UserForgetForm(forms.Form):
    '''这是用户忘记密码的表单类'''
    email=forms.EmailField(required=True)
    captcha=CaptchaField()

class UserResetForm(forms.Form):
    '''这是用户重置密码的表单类'''
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
    code=forms.CharField(required=True)

class UserPersonalCenterForm(forms.ModelForm):
    '''这是用户个人中心信息的表单类'''
    class Meta:
        model=UserProfile
        fields=['image','nickname','birthday','gender','address','phone']  

        def clean_phone(self):
            '''这是进一步验证手机的方法'''
            phone=self.cleaned_data['phone']
            com=re.compile(r'^1([358][0-9]|4[579]|66|7[0135678]|9[89])[0-9]{8}$')
            if com.match(phone):
                return phone
            #如果手机号不合法，就抛出异常
            else:
                raise forms.ValidationError('手机号码不合法')

class ChangeEmailForm(forms.Form):
    '''这是修改邮箱的表单类'''
    email=forms.EmailField(required=True,
    error_messages={
        'required':'邮箱不能为空'
    })
    password=forms.CharField(required=True,min_length=3,max_length=15,
    error_messages={
        'required':'密码不能为空',
        'min_length':'密码不能少于3位',
        'max_length':'密码不能多于15位'
    })

class ConfirmEmailForm(forms.Form):
    '''这是确认修改邮箱的表单类'''
    email=forms.EmailField(required=True,
    error_messages={
        'required':'邮箱不能为空'
    })
    code=forms.CharField(required=True,min_length=8,max_length=8,
    error_messages={
        'required':'验证码不能为空',
        'min_length':'验证码为8位',
        'max_length':'验证码为8位',
    })

class NewTopicForm(forms.Form):
    '''这是新建主题的表单类'''
    topic_name=forms.CharField(required=True,max_length=30,
    error_messages={
        'required':'主题不能为空',
        'max_length':'主题长度不能超过30个字',
    })

class NewBookmarkForm(forms.Form):
    '''这是新建收藏夹的表单类'''
    bookmark_name=forms.CharField(required=True,max_length=30,
    error_messages={
        'required':'收藏夹名不能为空',
        'max_length':'收藏夹名不能超过30个字',
    })

class NewBlogForm(forms.Form):
    '''这是验证新写的博客的表单类'''
    blog_title=forms.CharField(required=True,max_length=40,
    error_messages={
        'required':'博客标题不能为空',
        'max_length':'博客标题不能超过40个字',
    })

    blog_text=forms.CharField(required=True,widget=forms.Textarea,
    error_messages={
        'required':'博客正文不能为空'
    })

    blog_topic=forms.IntegerField(required=True,
    error_messages={
        'required':'博客主题不能为空'
    })
    
    category=forms.CharField(required=True,
    error_messages={
        'required':'博客分类不能为空'
    })