from django.shortcuts import render,redirect,reverse
from django.views import View
from .forms import UserRegisterForm,UserLoginForm,UserForgetForm,UserResetForm,UserPersonalCenterForm
from .models import UserProfile,EmailVerifyCode
from blogs.models import Topic,CollectBookMark
from blogs.models import Blog,Topic
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from tools.send_mail_tool import send_email_code
from django.http import HttpResponse
from datetime import datetime
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
                #对于没有激活的账号，先看看数据库里有没有用于激活的数据
                else:
                    evc_list=EmailVerifyCode.objects.filter(email=email,send_type=1)
                    if evc_list:
                        evc=evc_list[0]
                        #如果之前发过，需要检查发送时间间隔是否超过60秒
                        if (datetime.now()-evc.addtime).seconds>60:
                            evc.delete()
                            send_email_code(email,1)
                            return render(request,'users/login.html',{'msg':'您的账号还未激活，请立即前往您的邮箱激活','user_login_form':user_login_form})
                        #如果距离上次发送还不到60秒
                        else:
                            return render(request,'users/login.html',{'msg':'激活邮件已发送，请一分钟后重试','user_login_form':user_login_form})
                    #如果从来没有发过
                    else:
                        send_email_code(email,1)
                        return render(request,'users/login.html',{'msg':'您的账号还未激活，请立即前往您的邮箱激活','user_login_form':user_login_form})

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

class UserActivateView(View):
    '''这是激活用户账号的视图类'''
    def get(self,request,code):
        '''这是处理get请求的方法'''
        #先看看code是否传过来了
        if code:
            #然后查找该code是否在数据库里
            evc_list=EmailVerifyCode.objects.filter(code=code,send_type=1)
            if evc_list:
                evc=evc_list[0]
                #然后看看是否已经过期
                if (datetime.now()-evc.addtime).seconds<300:
                    email=evc.email
                    user=UserProfile.objects.filter(email=email)[0]
                    user.is_avd=True
                    user.save()
                    evc.delete()
                    #当一个用户被激活了，就给她创建默认主题和默认收藏夹
                    topic=Topic()
                    topic.owner=user
                    topic.topic_name='默认主题'
                    topic.is_default=True
                    topic.save()
                    collectbookmark=CollectBookMark()
                    collectbookmark.owner=user
                    collectbookmark.bookmark_name='默认收藏夹'
                    collectbookmark.is_default=True
                    collectbookmark.save()
                    return redirect(reverse('users:login'))
                else:
                    return HttpResponse('您的激活链接有误或已过期，请前往登录页面重试。')
            #如果验证码不在数据库里
            else:
                return HttpResponse('您的激活链接有误或已过期，请前往登录页面重试。')

class UserForgetView(View):
    '''这是用户忘记密码的视图类'''
    def get(self,request):
        user_forget_form=UserForgetForm()
        return render(request,'users/forget-passwd.html',{'user_forget_form':user_forget_form})
    def post(self,request):
        user_forget_form=UserForgetForm(request.POST)
        #如果格式合法,看看用户存不存在
        if user_forget_form.is_valid():
            email=user_forget_form.cleaned_data['email']
            user_list=UserProfile.objects.filter(email=email)
            #如果用户存在
            if user_list:
                #看看数据库里有没有该用户的重置密码验证码
                evc_list=EmailVerifyCode.objects.filter(email=email,send_type=2)
                #如果之前发过，看看时间间隔够不够
                if evc_list:
                    evc=evc_list[0]
                    #如果时间间隔超过了一分钟
                    if (datetime.now()-evc.addtime).seconds>60:
                        evc.delete()
                        send_email_code(email,2)
                        return render(request,'users/forget-passwd.html',{'msg':'请立即前往邮箱重置密码','user_forget_form':user_forget_form})
                    #如果时间间隔太近
                    else:
                        return render(request,'users/forget-passwd.html',{'msg':'邮件已发送，请一分钟后重试','user_forget_form':user_forget_form})
                #如果之前没有发过，直接发送
                else:
                    send_email_code(email,2)
                    return render(request,'users/forget-passwd.html',{'msg':'请立即前往邮箱重置密码','user_forget_form':user_forget_form})
            #如果用户不存在
            else:
                return render(request,'users/forget-passwd.html',{'msg':'用户不存在','user_forget_form':user_forget_form})
        #如果格式不合法
        return render(request,'users/forget-passwd.html',{'user_forget_form':user_forget_form})
                
class UserResetView(View):
    '''这是用户重置密码的视图类'''
    def get(self,request,code):
        if code:
            evc_list=EmailVerifyCode.objects.filter(code=code,send_type=2)
            if evc_list:
                evc=evc_list[0]
                if (datetime.now()-evc.addtime).seconds<300:
                    return render(request,'users/reset-passwd.html',{'code':code})
                else:
                    return HttpResponse('您的重置密码链接已过期，请前往登录页面重试。')
            else:
                return HttpResponse('您的重置密码链接有误或已过期，请前往登录页面重试。')
            
    def post(self,request,code):
        user_reset_form=UserResetForm(request.POST)
        if user_reset_form.is_valid():
            password=user_reset_form.cleaned_data['password']
            password1=user_reset_form.cleaned_data['password1']
            if password==password1:
                code=user_reset_form.cleaned_data['code']
                evc=EmailVerifyCode.objects.filter(code=code,send_type=2)[0]
                if (datetime.now()-evc.addtime).seconds<300:
                    email=evc.email
                    user=UserProfile.objects.filter(email=email)[0]
                    user.set_password(password)
                    user.save()
                    evc.delete()
                    return redirect(reverse('users:login'))
                #如果链接过期了
                else:
                    return HttpResponse('您的重置密码链接已过期，请前往登录页面重试。')
            #如果密码不一致
            else:
                return render(request,'users/reset-passwd.html',{'msg':'两次输入的密码不一致','user_reset_form':user_reset_form,'code':code})
        #如果格式不合法
        else:
            return render(request,'users/reset-passwd.html',{'user_reset_form':user_reset_form,'code':code})
        
class UserPersonalCenterView(View):
    '''这是用户个人中心首页的视图类'''
    def get(self,request):
        return render(request,'users/personal-center.html')
    def post(self,request):
        #因为是修改信息，所有里面需要有instance参数
        user_pc_form=UserPersonalCenterForm(request.POST,request.FILES,instance=request.user)
        if user_pc_form.is_valid():
            user_pc_form.save()
            return render(request,'users/personal-center.html',{'msg':'修改成功'})
        else:
            return render(request,'users/personal-center.html',{'user_pc_form':user_pc_form,'msg':'修改失败'})

class MyblogsView(View):
    '''这是我的博客的视图类'''
    def get(self,request):
        topic_list=Topic.objects.filter(owner=request.user).order_by('addtime')
        blog_list=Blog.objects.filter(author=request.user)
        start=request.user.addtime
        end=datetime.now()
        month_num=12*(end.year-start.year)+end.month-start.month
        time_list=[]
        year=start.year
        month=start.month
        for m in range(month_num+1):
            time_list.append([year,month])
            month+=1
            if month==13:
                month=1
                year+=1
        time_list.reverse()
        return render(request,'users/personal-center-myblogs.html',{'topic_list':topic_list,'blog_list':blog_list,'time_list':time_list})

        
