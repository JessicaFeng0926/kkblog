from django.db import models
from users.models import UserProfile
from blogs.models import Blog
from blogs.models import CollectBookMark

# Create your models here.

class UserCollect(models.Model):
    '''这是用户收藏的模型类'''
    collector=models.ForeignKey(UserProfile,verbose_name='收藏者',on_delete=models.CASCADE)
    collect_blog=models.ForeignKey(Blog,verbose_name='被收藏博客',on_delete=models.CASCADE)
    bookmark=models.ForeignKey(CollectBookMark,verbose_name='所属收藏夹',on_delete=models.CASCADE)
    cstatus=models.BooleanField(verbose_name='是否收藏',default=True)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')

    def __str__(self):
        '''返回的描述'''
        return self.collector.username

    class Meta:
        '''这是元信息类'''
        verbose_name='收藏信息'
        verbose_name_plural=verbose_name

class UserFollow(models.Model):
    '''这是用户关注的模型类'''
    oneself=models.ForeignKey(UserProfile,verbose_name='小粉丝',on_delete=models.CASCADE)
    idol_id=models.IntegerField(verbose_name='偶像的id')
    fstatus=models.BooleanField(verbose_name='是否关注',default=True)
    is_mutual=models.BooleanField(verbose_name='是否互关',default=False)
    is_read=models.BooleanField(verbose_name='是否已读',default=False)
    is_delete=models.BooleanField(verbose_name='是否删除',default=False)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')

    def __str__(self):
        '''这是返回的描述'''
        return self.oneself.username
    class Meta:
        verbose_name='关注信息'
        verbose_name_plural=verbose_name

class UserThumbup(models.Model):
    '''这是点赞的模型类'''
    oneself=models.ForeignKey(UserProfile,verbose_name='点赞者',on_delete=models.CASCADE)
    thumbup_blog=models.ForeignKey(Blog,verbose_name='被赞的博客',on_delete=models.CASCADE)
    tstatus=models.BooleanField(verbose_name='是否赞',default=True)
    is_read=models.BooleanField(verbose_name='是否已读',default=False)
    is_delete=models.BooleanField(verbose_name='是否删除',default=False)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')
    
    def __str__(self):
        '''这是返回的描述'''
        return self.oneself.username

    class Meta:
        '''这是元信息类'''
        verbose_name='点赞信息'
        verbose_name_plural=verbose_name

class UserNotice(models.Model):
    '''这是系统通知的模型类'''
    recipient=models.ForeignKey(UserProfile,verbose_name='被通知人',on_delete=models.CASCADE)
    notice_content=models.TextField(verbose_name='通知内容')
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')
    is_read=models.BooleanField(verbose_name='是否已读',default=False)
    is_delete=models.BooleanField(verbose_name='是否删除',default=False)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')

    def __str__(self):
        '''这是返回的描述'''
        return self.recipient.username

    class Meta:
        '''这是元信息类'''
        verbose_name='系统通知信息'
        verbose_name_plural=verbose_name

class UserComment(models.Model):
    '''这是用户评论的模型类'''
    comment_blog=models.ForeignKey(Blog,verbose_name='被评论的博客',on_delete=models.CASCADE)
    speaker=models.ForeignKey(UserProfile,verbose_name='评论发出者',on_delete=models.CASCADE)
    listener_id=models.IntegerField(verbose_name='评论接收者')
    comment_content=models.CharField(max_length=100,verbose_name='评论内容')
    listener_read=models.BooleanField(verbose_name='评论接收者是否已读',default=False)
    author_read=models.BooleanField(verbose_name='博主是否已读',default=False)
    listener_del=models.BooleanField(verbose_name='评论接收者是否删除',default=False)
    author_del=models.BooleanField(verbose_name='博主是否删除',default=False)
    is_delete=models.BooleanField(verbose_name='是否删除',default=False)
    addtime=models.DateTimeField(verbose_name='添加时间',auto_now_add=True)

    def __str__(self):
        '''这是返回的描述'''
        return self.speaker.username

    class Meta:
        '''这是元信息类'''
        verbose_name='评论信息'
        verbose_name_plural=verbose_name

    