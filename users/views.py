from django.shortcuts import render,redirect,reverse
from django.views import View
from .forms import UserRegisterForm,UserLoginForm
from .models import UserProfile
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from tools.send_mail_tool import send_email_code
# Create your views here.

def index(request):
    '''这是主页的视图'''
    return render(request,'index.html')

class UserLoginView(View):
    '''这是用户登录的视图'''
    def get(self,request):
        '''这是get请求方式的处理方法'''
        return render(request,'users/login.html')
    def post(self,request):
        '''这是post请求的处理方法'''
        user_login_form=UserLoginForm(request.POST)
        #先看看用户的输入是否合法,合法就看看用户的邮箱和密码是否正确
        if user_login_form.is_valid():
            email=user_login_form.cleaned_data['email']
            password=user_login_form.cleaned_data['password']
            user=authenticate(username=email,password=password)
            #如果账号密码都正确，看看是否激活了
            if user:
                if user.is_avd:
                    login(request,user)
                    return redirect(reverse('index'))
                else:
                    send_email_code(email,1)
                    return render(request,'users/login.html',{'msg':'您的账号还未激活，请前往您的邮箱激活','user_login_form':user_login_form})
            else:
                return render(request,'users/login.html',{'msg':'邮箱或密码错误','user_login_form':user_login_form})
                
            
        #不合法，就把带有错误信息的表单返回去
        else:
            return render(request,'users/login.html',{'user_login_form':user_login_form})
            

class UserRegisterView(View):
    '''这是用户注册的视图'''
    def get(self,request):
        '''这是get请求方式的处理方法'''
        #这时把这个表单类的实例传给模板是为了使用里面的capcha
        user_register_form=UserRegisterForm()
        return render(request,'users/register.html',{'user_register_form':user_register_form})

    def post(self,request):
        '''这是处理post请求的方法'''
        user_register_form=UserRegisterForm(request.POST)
        #验证是否合法
        if user_register_form.is_valid():
            #如果合法，就看看用户是否已经存在
            email=user_register_form.cleaned_data['email']
            user_list=UserProfile.objects.filter(Q(username=email)|Q(email=email))
            #如果用户已经存在，告知已经存在
            if user_list:
                return render(request,'users/register.html',{'msg':'用户已经存在','user_register_form':user_register_form})
            #不存在，就看看两次密码是否一样
            else:
                password=user_register_form.cleaned_data['password']
                password1=user_register_form.cleaned_data['password1']
                #两次密码一样，可以注册了
                if password==password1:
                    new_user=UserProfile()
                    new_user.username=email
                    new_user.email=email
                    new_user.set_password(password)
                    new_user.save()
                    return redirect(reverse('index'))
                #两次密码不一样，要返回信息
                else:
                    return render(request,'users/register.html',{'msg':'两次输入的密码不一致','user_register_form':user_register_form})        

        #如果不合法，就把用户提交的表单信息返回，并且里面已经包含了我们验证的时候产生的错误信息
        else:
            return render(request,'users/register.html',{'user_register_form':user_register_form})

class UserLogoutView(View):
    '''这是用户退出的视图类'''
    def get(self,request):
        logout(request)
        return redirect(reverse('index'))
