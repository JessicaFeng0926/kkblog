from django.db import models
#导入抽象用户类用于我自己的用户继承
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UserProfile(AbstractUser):
    '''这是用户信息的模型类'''
    image=models.ImageField(verbose_name='用户头像',upload_to='user/',max_length=200,null=True,blank=True)
    nickname=models.CharField(max_length=20,verbose_name='用户昵称',null=True,blank=True)
    birthday=models.DateField(verbose_name='用户生日',null=True,blank=True)
    gender=models.CharField(choices=(('girl','女'),('boy','男')),verbose_name='用户性别',max_length=10,default='girl')
    phone=models.CharField(verbose_name='用户手机',max_length=11,null=True,blank=True)
    address=models.CharField(verbose_name='用户地址',max_length=200,null=True,blank=True)
    is_avd=models.BooleanField(verbose_name='是否激活',default=False)
    visit_num=models.IntegerField(verbose_name='博客访问量',default=0)
    follow_num=models.IntegerField(verbose_name='关注数',default=0)
    fan_num=models.IntegerField(verbose_name='粉丝数',default=0)
    thumb_num=models.IntegerField(verbose_name='点赞数',default=0)
    comment_num=models.IntegerField(verbose_name='评论数',default=0)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='注册时间')

    def __str__(self):
        '''这是返回的描述'''
        return self.username
    
    def get_count(self):
        '''这里返回未读消息的数量'''
        from operations.models import UserThumbup,UserFollow,UserComment,UserNotice
        from blogs.models import Blog
        from django.db.models import Q
        follow_num=UserFollow.objects.filter(idol_id=self.id,fstatus=True,is_delete=False,is_read=False).count()
        notice_num=UserNotice.objects.filter(recipient_id=self.id,is_delete=False,is_read=False).count()
        blog_list=Blog.objects.filter(author_id=self.id,is_delete=False)
        thumb_num=UserThumbup.objects.filter(thumbup_blog__in=blog_list,tstatus=True,is_delete=False,is_read=False).count()
        usercomment_list=UserComment.objects.filter(Q(listener_id=self.id)|Q(comment_blog__in=blog_list),is_delete=False)
        comment_num=0
        for comment in usercomment_list:
            if comment.comment_blog.author == self:
                if not comment.author_read and not comment.author_del:
                    comment_num+=1
            else:
                if not comment.listener_read and not comment.listener_del:
                    comment_num+=1
        return follow_num+notice_num+thumb_num+comment_num

    class Meta:
        '''这是元信息类'''
        verbose_name='用户信息'
        verbose_name_plural=verbose_name

class EmailVerifyCode(models.Model):
    '''这是邮箱验证码模型类'''
    code=models.CharField(max_length=20,verbose_name='邮箱验证码')
    email=models.EmailField(verbose_name='用户邮箱',max_length=200)
    send_type=models.IntegerField(choices=((1,'register'),(2,'forget'),(3,'change')),verbose_name='验证类型')
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')

    def __str__(self):
        '''这是返回的描述'''
        return self.code
    
    class Meta:
        '''这是元信息类'''
        verbose_name='邮箱验证码'
        verbose_name_plural=verbose_name

