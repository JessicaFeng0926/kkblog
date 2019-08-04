from django.shortcuts import render,redirect,reverse
from django.views import View
from .forms import UserRegisterForm,UserLoginForm,UserForgetForm,UserResetForm,UserPersonalCenterForm,NewTopicForm,NewBookmarkForm,NewBlogForm,ChangeEmailForm
from .models import UserProfile,EmailVerifyCode
from blogs.models import Topic,CollectBookMark,Blog
from operations.models import UserThumbup,UserFollow,UserCollect,UserComment,UserNotice
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from tools.send_mail_tool import send_email_code
from django.http import HttpResponse
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from datetime import datetime
# Create your views here.

def index(request):
    '''这是主页的视图'''
    #按照点击量返回最热博客（这是默认的最热）
    blog_list=Blog.objects.filter(is_delete=False).order_by('-click_num')
    #如果传来了按照最新或最热来排序，就重新排序
    sort=request.GET.get('sort','')
    if sort:
        if sort=='new':
            blog_list=blog_list.order_by('-addtime')
        else:
            blog_list=blog_list.order_by('-click_num')
    #如果传来了博客分类，就要重新筛选
    category=request.GET.get('category','')
    if category:
        blog_list=blog_list.filter(category=category)

    #如果传来了搜索的关键词，就要重新筛选
    search=request.GET.get('search','')
    if search:
        blog_list=blog_list.filter(Q(blog_text__icontains=search)|Q(blog_title__icontains=search))
    
    blog_list=blog_list[:100]

    #给博客分页
    pa=Paginator(blog_list,20)
    pagenum=request.GET.get('pagenum','')
    try:
        current_page=pa.get_page(pagenum)
    except PageNotAnInteger:
        current_page=pa.get_page(1)
    except EmptyPage:
        current_page=pa.get_page(pa.num_pages)

    #按照访问量返回热门博主
    author_list=UserProfile.objects.exclude(is_superuser=True).order_by('-visit_num')[:5]

    return render(request,'index.html',{'author_list':author_list,'current_page':current_page,'sort':sort,'category':category,'search':search})

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

class ChangeEmailView(View):
    '''这是修改邮箱的视图类'''
    def get(self,request):
        return render(request,'users/change-email.html')
    def post(self,request):
        changeemail_form=ChangeEmailForm(request.POST)
        if changeemail_form.is_valid():
            email=changeemail_form.cleaned_data['email']
            password=changeemail_form.cleaned_data['password']
            user_list=UserProfile.objects.filter(email=email)
            if user_list:
                return render(request,'users/change-email.html',{'changeemail_form':changeemail_form,'msg':'邮箱已经被占用'})
            else:
                user=authenticate(username=request.user.username,password=password)
                if user:
                    send_email_code(email,3)
                    return redirect(reverse('users:confirm_email'))
                else:
                    return render(request,'users/change-email.html',{'changeemail_form':changeemail_form,'msg':'密码错误'})

        else:
            return render(request,'users/change-email.html',{'changeemail_form':changeemail_form})

class ConfirmEmailView(View):
    '''这是确认修改邮箱的视图类'''
    def get(self,request):
        return render(request,'users/confirm-email.html')
    def post(self,request):
        pass

def get_data_list(user):
    '''这是我的博客页面获取需要的所有信息的函数'''
    topic_list=Topic.objects.filter(owner=user,is_delete=False).order_by('addtime')
    blog_list=Blog.objects.filter(author=user,is_delete=False).order_by('addtime')
    """ #因为不需要显示没有写博客的月份，所以其实日期不用注册时间了，用第一篇博客的创作时间
    start=blog_list[0].addtime
    end=datetime.now()
    month_num=12*(end.year-start.year)+end.month-start.month
    time_list=[]
    year=start.year
    month=start.month
    #b是我们遍历blog_list的起点，因为已经遍历过的就不想重复遍历，所以b会随着count一起增长
    b=0
    for m in range(month_num+1):
        #count用于计算本月份有多少篇博客
        count=0
        for blog in blog_list[b:]:
            if blog.addtime.year==year and blog.addtime.month==month:
                count+=1
        #当本月的博客数量不为0时，把这个月份和这个月的博客数作为数据传回前端
        if count!=0:
            time_list.append([year,month,count])
        b+=count
        month+=1
        if month==13:
            month=1
            year+=1 """
    #以第一篇博客的年和月开头
    time_list=[]
    if blog_list:
        year=blog_list[0].addtime.year
        month=blog_list[0].addtime.month
        #count是快指针，year和month是慢指针
        count=0
        
        for blog in blog_list:
            if blog.addtime.year==year and blog.addtime.month==month:
                count+=1
            else:
                time_list.append([year,month,count])
                count=1
                year=blog.addtime.year
                month=blog.addtime.month
        #别忘了最后还要append一次，因为最后的那个年和月不会再有别的年月跟它比较了，走不到else分支，所以没办法在循环内append
        time_list.append([year,month,count])
        time_list.reverse()
    
    blog_list=blog_list.order_by('-addtime')
    return [topic_list,blog_list,time_list]


class MyblogsView(View):
    '''这是我的博客的视图类'''
    def get(self,request):
        #下面是默认需要获取的全部数据，包括全部主题，全部博客和全部月份
        data_list=get_data_list(request.user)
        topic_list=data_list[0]
        blog_list=data_list[1]
        time_list=data_list[2]
        #如果用户点击了某个主题，那么就按照主题进一步筛选该主题下的博客
        topic_id=request.GET.get('topic','')
        if topic_id:
            topic_id=int(topic_id)
            blog_list=blog_list.filter(blog_topic_id=topic_id)
        #如果用户点击了某个月份，就要删选这个月的博客
        year=request.GET.get('year','')
        month=request.GET.get('month','')
        if year and month:
            year=int(year)
            month=int(month)
            blog_list_copy=blog_list[:]
            blog_list=[]
            for blog in blog_list_copy:
                if blog.addtime.year==year and blog.addtime.month==month:
                    blog_list.append(blog)

        #分页
        pa=Paginator(blog_list,20)
        pagenum=request.GET.get('pagenum','')
        try:
            current_page=pa.get_page(pagenum)
        except PageNotAnInteger:
            current_page=pa.get_page(1)
        except EmptyPage:
            current_page=pa.get_page(pa.num_pages)
        return render(request,'users/personal-center-myblogs.html',{'topic_list':topic_list,'blog_list':blog_list,'time_list':time_list,'topic_id':topic_id,'year':year,'month':month,'current_page':current_page})
    def post(self,request):
        '''这是处理用户post新建话题的方法'''
        new_topic_form=NewTopicForm(request.POST)
        data_list=get_data_list(request.user)
        topic_list=data_list[0]
        blog_list=data_list[1]
        time_list=data_list[2]
        if new_topic_form.is_valid():
            topic_name=new_topic_form.cleaned_data['topic_name']
            new_topic=Topic()
            new_topic.topic_name=topic_name
            new_topic.owner=request.user
            new_topic.save()
            return render(request,'users/personal-center-myblogs.html',{'topic_list':topic_list,'blog_list':blog_list,'time_list':time_list})
        else:
            return render(request,'users/personal-center-myblogs.html',{'new_topic_form':new_topic_form,'topic_list':topic_list,'blog_list':blog_list,'time_list':time_list})
        
class MyBlogDetailView(View):
    '''这是我的博客详情的视图类'''
    def get(self,request,blog_id):
        if blog_id:
            blog_list=Blog.objects.filter(id=int(blog_id),is_delete=False)
            if blog_list:
                blog=blog_list[0]
                #本篇博客和博主的点击量都加一
                blog.click_num+=1
                blog.save()
                blog.author.visit_num+=1
                blog.author.save()
                data_list=get_data_list(request.user)
                topic_list=data_list[0]
                time_list=data_list[2]

                #获取博主对这篇博客的点赞状态
                tstatus=False
                user_thumbup_list=UserThumbup.objects.filter(oneself=request.user,thumbup_blog=blog,tstatus=True)
                if user_thumbup_list:
                    tstatus=True

                #获取本篇博客的所有评论
                usercomment_list=UserComment.objects.filter(comment_blog=blog,is_delete=False).order_by('-addtime')
                for usercomment in usercomment_list:
                    usercomment.listener=UserProfile.objects.filter(id=usercomment.listener_id)[0]

                return render(request,'users/personal-center-myblog-detail.html',{'blog':blog,'topic_list':topic_list,'time_list':time_list,'tstatus':tstatus,'usercomment_list':usercomment_list})
            else:
                return redirect(reverse('users:myblogs'))

    def post(self,request,blog_id):
        new_topic_form=NewTopicForm(request.POST)
        blog=Blog.objects.filter(id=int(blog_id))[0]
        data_list=get_data_list(request.user)
        topic_list=data_list[0]
        time_list=data_list[2]
        if new_topic_form.is_valid():
            topic_name=new_topic_form.cleaned_data['topic_name']
            new_topic=Topic()
            new_topic.topic_name=topic_name
            new_topic.owner=request.user
            new_topic.save()
            return render(request,'users/personal-center-myblog-detail.html',{'topic_list':topic_list,'time_list':time_list,'blog':blog})
        else:
            return render(request,'users/personal-center-myblog-detail.html',{'blog':blog,'topic_list':topic_list,'time_list':time_list,'new_topic_form':new_topic_form})

class MyFollowView(View):
    '''这是我的关注页面的视图类'''
    def get(self,request):
        current_page=[]

        #先看看用户有没有关注别人
        userfollow_list=UserFollow.objects.filter(oneself=request.user,fstatus=True).order_by('-addtime')
        if userfollow_list:
            #有关注的人，就拿到所有关注人的id
            idolid_list=[ userfollow.idol_id for userfollow in userfollow_list]
            idol_list=UserProfile.objects.filter(id__in=idolid_list)
            for idol in idol_list:
                reverseuserfollow=UserFollow.objects.filter(oneself=idol,idol_id=request.user.id,fstatus=True)
                if reverseuserfollow:
                    idol.is_mutual=True
                else:
                    idol.is_mutual=False
            
            #分页
            pa=Paginator(idol_list,30)
            pagenum=request.GET.get('pagenum','')
            try:
                current_page=pa.get_page(pagenum)
            except PageNotAnInteger:
                current_page=pa.get_page(1)
            except EmptyPage:
                current_page=pa.get_page(pa.num_pages)
        return render(request,'users/personal-center-following.html',{'current_page':current_page})

class MyFansView(View):
    '''这是我的粉丝的视图类'''
    def get(self,request):
        current_page=[]
        #先看看有没有人关注我
        userfollow_list=UserFollow.objects.filter(idol_id=request.user.id,fstatus=True)
        #如果有，就把这些人都拿出来
        if userfollow_list:
            fan_list=[userfollow.oneself for userfollow in userfollow_list]
            #再看看用户关没关注他的粉丝们，把互关状态添加进去
            for fan in fan_list:
                reverseuserfollow=UserFollow.objects.filter(oneself=request.user,idol_id=fan.id,fstatus=True)
                if reverseuserfollow:
                    fan.is_mutual=True
                else:
                    fan.is_mutual=False
            #分页
            pa=Paginator(fan_list,30)
            pagenum=request.GET.get('pagenum','')
            try:
                current_page=pa.get_page(pagenum)
            except PageNotAnInteger:
                current_page=pa.get_page(1)
            except EmptyPage:
                current_page=pa.get_page(pa.num_pages)
        return render(request,'users/personal-center-followers.html',{'current_page':current_page})

class MyCollectionsView(View):
    '''这是我的收藏的视图类'''
    def get(self,request):
        blog_list=[]
        usercollect_list=UserCollect.objects.filter(collector=request.user,cstatus=True).order_by('-addtime')
        #如果有收藏记录
        if usercollect_list:
            #如果用户点击了某个收藏夹，就要进一步筛选只属于这个收藏夹的博客
            bookmark_id=request.GET.get('bookmark','')
            if bookmark_id:
                bookmark_id=int(bookmark_id)
                usercollect_list=usercollect_list.filter(bookmark_id=bookmark_id)

            blog_list=[usercollect.collect_blog for usercollect in usercollect_list]
        
        #分页
        pa=Paginator(blog_list,20)
        pagenum=request.GET.get('pagenum','')
        try:
            current_page=pa.get_page(pagenum)
        except PageNotAnInteger:
            current_page=pa.get_page(1)
        except EmptyPage:
            current_page=pa.get_page(pa.num_pages)
        #如果该用户从未收藏过任何博客，他也可以点收藏夹点着玩儿,还是要把收藏夹的id传回去
        bookmark_id=request.GET.get('bookmark','')
        if bookmark_id:
            bookmark_id=int(bookmark_id)

        #找出所有的收藏夹信息
        bookmark_list=CollectBookMark.objects.filter(owner=request.user,is_delete=False)
        
        return render(request,'users/personal-center-mycollections.html',{'current_page':current_page,'bookmark_list':bookmark_list,'bookmark_id':bookmark_id})
    def post(self,request):
        '''这是处理新建收藏夹的方法'''
        blog_list=[]
        usercollect_list=UserCollect.objects.filter(collector=request.user,cstatus=True)
        if usercollect_list:
            blog_list=[usercollect.collect_blog for usercollect in usercollect_list]

        #找出所有的收藏夹信息
        bookmark_list=CollectBookMark.objects.filter(owner=request.user,is_delete=False)
        #生成新收藏夹表单对象
        new_bookmark_form=NewBookmarkForm(request.POST)
        #看看是否有效
        if new_bookmark_form.is_valid():
            bookmark_name=new_bookmark_form.cleaned_data['bookmark_name']
            new_bookmark=CollectBookMark()
            new_bookmark.bookmark_name=bookmark_name
            new_bookmark.owner=request.user
            new_bookmark.save()
            return render(request,'users/personal-center-mycollections.html',{'blog_list':blog_list,'bookmark_list':bookmark_list})
        else:
            return render(request,'users/personal-center-mycollections.html',{'new_bookmark_form':new_bookmark_form,'blog_list':blog_list,'bookmark_list':bookmark_list})

class WriteBlogView(View):
    '''这是写博客的视图类'''
    def get(self,request):
        #把用户的所有主题传过去
        topic_list=Topic.objects.filter(owner=request.user,is_delete=False)
        return render(request,'users/write-blog.html',{'topic_list':topic_list})
    def post(self,request):
        newblog_form=NewBlogForm(request.POST)
        topic_list=Topic.objects.filter(owner=request.user,is_delete=False)
        if newblog_form.is_valid():
            blog_title=newblog_form.cleaned_data['blog_title']
            blog_text=newblog_form.cleaned_data['blog_text']
            blog_topic_id=int(newblog_form.cleaned_data['blog_topic'])
            category=newblog_form.cleaned_data['category']
            newblog=Blog()
            newblog.blog_title=blog_title
            newblog.blog_text=blog_text
            newblog.blog_topic_id=blog_topic_id
            newblog.category=category
            newblog.author=request.user
            newblog.save()
            return redirect('users:myblogs')
        else:
            return render(request,'users/write-blog.html',{'topic_list':topic_list,'newblog_form':newblog_form})

class EditBlogView(View):
    '''这是修改博客的视图类'''
    def get(self,request,blog_id):
        if blog_id:
            blog_list=Blog.objects.filter(id=int(blog_id),is_delete=False)
            if blog_list:
                blog=blog_list[0]
                #\r\n在js里会报错，所以这里把它们替换成空再传回前端
                #换行效果依然存在，因为富文本里的每一段都用p标签包裹起来了，换行符实在是鸡肋
                blog.blog_text=blog.blog_text.replace('\r\n','')
                #把用户的主题列表也传回去
                topic_list=Topic.objects.filter(owner=request.user,is_delete=False)
                return render(request,'users/edit-blog.html',{'blog':blog,'topic_list':topic_list})
            #如果博客不存在，重定向到我的博客列表页
            else:
                return redirect(reverse('users:myblogs'))
    def post(self,request,blog_id):
        editblog_form=NewBlogForm(request.POST)
        if editblog_form.is_valid():
            blog_title=editblog_form.cleaned_data['blog_title']
            blog_text=editblog_form.cleaned_data['blog_text']
            blog_topic=editblog_form.cleaned_data['blog_topic']
            category=editblog_form.cleaned_data['category']
            blog=Blog.objects.filter(id=int(blog_id))[0]
            blog.blog_title=blog_title
            blog.blog_text=blog_text
            blog.blog_topic_id=blog_topic
            blog.category=category
            blog.save()
            return redirect(reverse('users:myblogs'))
        else:
            blog=Blog.objects.filter(id=int(blog_id))[0]
            blog.blog_text=blog.blog_text.replace('\r\n','')
            topic_list=Topic.objects.filter(owner=request.user,is_delete=False)
            return render(request,'users/edit-blog.html',{'blog':blog,'topic_list':topic_list,'editblog_form':editblog_form})

class CollectionMoveView(View):
    '''这是移动收藏的博客的视图类'''
    def get(self,request,blog_id):
        if blog_id:
            #先看看要移动的博客是否在收藏记录里面
            usercollect_list=UserCollect.objects.filter(collector=request.user,collect_blog_id=int(blog_id),cstatus=True)
            #存在就返回所有收藏夹的名字，以及这条收藏记录
            if usercollect_list:
                usercollect=usercollect_list[0]
                bookmark_list=CollectBookMark.objects.filter(owner=request.user,is_delete=False)
                return render(request,'users/personal-center-mycollection-move.html',{'usercollect':usercollect,'bookmark_list':bookmark_list})
            #不存在就重定向到我的收藏页面
            else:
                return redirect(reverse('users:mycollections'))
    def post(self,request,blog_id):
        '''因为这个页面有两个form，
        所以我把这个post用作处理新建主题，
        移动的在operations里面有个单独的视图'''
        new_bookmark_form=NewBookmarkForm(request.POST)
        #还要获取用户的这条收藏记录以及所有的收藏夹
        usercollect=UserCollect.objects.filter(collector=request.user,collect_blog_id=int(blog_id),cstatus=True)[0]
        bookmark_list=CollectBookMark.objects.filter(owner=request.user,is_delete=False)
        if new_bookmark_form.is_valid():
            bookmark_name=new_bookmark_form.cleaned_data['bookmark_name']
            new_bookmark=CollectBookMark()
            new_bookmark.bookmark_name=bookmark_name
            new_bookmark.owner=request.user
            new_bookmark.save()
            return render(request,'users/personal-center-mycollection-move.html',{'usercollect':usercollect,'bookmark_list':bookmark_list})
        #无效就记得把表单类对象也传回去，里面包含错误信息
        else:
            return render(request,'users/personal-center-mycollection-move.html',{'usercollect':usercollect,'bookmark_list':bookmark_list,'new_bookmark_form':new_bookmark_form})

class MessagesView(View):
    '''这是我的消息的视图类'''
    def get(self,request):
        #所有的关注
        userfollow_list=UserFollow.objects.filter(idol_id=request.user.id,fstatus=True,is_delete=False).order_by('-addtime')
        
        #所有的赞
        blog_list=Blog.objects.filter(author=request.user,is_delete=False)
        userthumb_list=UserThumbup.objects.filter(thumbup_blog__in=blog_list,tstatus=True,is_delete=False).order_by('-addtime')

        #所有的评论
        usercomment_list=UserComment.objects.filter(Q(listener_id=request.user.id)|Q(comment_blog__in=blog_list),is_delete=False).order_by('-addtime')

        #所有的系统通知
        usernotice_list=UserNotice.objects.filter(recipient=request.user,is_delete=False).order_by('-addtime')
        
        #未读的赞的数量
        thumb_num=userthumb_list.filter(is_read=False).count()
        #未读的关注的数量
        follow_num=userfollow_list.filter(is_read=False).count()
        #未读的系统通知的数量
        notice_num=usernotice_list.filter(is_read=False).count()
        #未读的评论的数量
        comment_num=0
        for comment in usercomment_list:
            if comment.comment_blog.author == request.user:
                if not comment.author_read and not comment.author_del:
                    comment_num+=1
            else:
                if not comment.listener_read and not comment.listener_del:
                    comment_num+=1

        #如果用户传来了分类，那就重新筛选
        sort=request.GET.get('sort')
        if sort:
            if sort == 'comment':
                userfollow_list=userfollow_list.filter(addtime=datetime(1969,6,7))
                userthumb_list=userthumb_list.filter(addtime=datetime(1969,6,7))
                usernotice_list=usernotice_list.filter(addtime=datetime(1969,6,7))
            elif sort == 'thumb':
                usercomment_list=usercomment_list.filter(addtime=datetime(1969,6,7))
                userfollow_list=userfollow_list.filter(addtime=datetime(1969,6,7))
                usernotice_list=usernotice_list.filter(addtime=datetime(1969,6,7))
            elif sort == 'follow':
                usercomment_list=usercomment_list.filter(addtime=datetime(1969,6,7))
                userthumb_list=userthumb_list.filter(addtime=datetime(1969,6,7))
                usernotice_list=usernotice_list.filter(addtime=datetime(1969,6,7))
            elif sort == 'notice':
                usercomment_list=usercomment_list.filter(addtime=datetime(1969,6,7))
                userthumb_list=userthumb_list.filter(addtime=datetime(1969,6,7))
                userfollow_list=userfollow_list.filter(addtime=datetime(1969,6,7))
        
        #按照用户传来的已读未读状态来筛选
        read=request.GET.get('read','')
        if read == 'no':
            usercomment_list_copy=usercomment_list[:]
            usercomment_list=[]
            for usercomment in usercomment_list_copy:
                #如果评论的是我的博客，author是我，listenr不一定是我，我能控制的是author的阅读状态
                if usercomment.comment_blog.author_id ==  request.user.id:
                    if not usercomment.author_read and not usercomment.author_del:
                        usercomment_list.append(usercomment)
                #如果评论的是别人的博客，listener是我，author不是我，我能控制的是listener的阅读状态
                else:
                    if not usercomment.listener_read and not usercomment.listener_del:
                        usercomment_list.append(usercomment)
            for usercomment in usercomment_list:
                usercomment.is_read = False
            userfollow_list=userfollow_list.filter(is_read=False)
            userthumb_list=userthumb_list.filter(is_read=False)
            usernotice_list=usernotice_list.filter(is_read=False)
        elif read == 'yes':
            usercomment_list_copy=usercomment_list[:]
            usercomment_list=[]
            for usercomment in usercomment_list_copy:
                if usercomment.comment_blog.author_id == request.user.id:
                    if usercomment.author_read and not usercomment.author_del:
                        usercomment_list.append(usercomment)
                else:
                    if usercomment.listener_read and not usercomment.listener_del:
                        usercomment_list.append(usercomment)
            for usercomment in usercomment_list:
                usercomment.is_read=True
            userfollow_list=userfollow_list.filter(is_read=True)
            userthumb_list=userthumb_list.filter(is_read=True)
            usernotice_list=usernotice_list.filter(is_read=True)
        else:
            usercomment_list_copy=usercomment_list[:]
            usercomment_list=[]
            for usercomment in usercomment_list_copy:
                if usercomment.comment_blog.author == request.user and not usercomment.author_del:
                    if usercomment.author_read:
                        usercomment.is_read=True
                    else:
                        usercomment.is_read=False
                    usercomment_list.append(usercomment)
                elif usercomment.comment_blog.author != request.user and not usercomment.listener_del:
                    if usercomment.listener_read:
                        usercomment.is_read=True
                    else:
                        usercomment.is_read=False
                    usercomment_list.append(usercomment)
        #把所有数据放到一起，以便于分页
        data_list=[]
        for usercomment in usercomment_list:
            usercomment.type = 'c'
            data_list.append(usercomment)
        for usernotice in usernotice_list:
            usernotice.type= 'n'
            data_list.append(usernotice)
        for userthumb in userthumb_list:
            userthumb.type = 't'
            data_list.append(userthumb)
        for userfollow in userfollow_list:
            userfollow.type = 'f'
            data_list.append(userfollow)
        
        #分页
        pa=Paginator(data_list,20)
        pagenum=request.GET.get('pagenum','')
        try:
            current_page=pa.get_page(pagenum)
        except PageNotAnInteger:
            current_page=pa.get_page(1)
        except EmptyPage:
            current_page=pa.get_page(pa.num_pages)
        
        return render(request,'users/personal-center-messages.html',{'userfollow_list':userfollow_list,'userthumb_list':userthumb_list,'usercomment_list':usercomment_list,'usernotice_list':usernotice_list,'sort':sort,'read':read,'follow_num':follow_num,'notice_num':notice_num,'thumb_num':thumb_num,'comment_num':comment_num,'current_page':current_page})
            
        