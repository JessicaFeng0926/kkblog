from django.db import models
from users.models import UserProfile

# Create your models here.
class Topic(models.Model):
    '''这是主题的模型类'''
    owner=models.ForeignKey(UserProfile,verbose_name='主题拥有者',on_delete=models.CASCADE)
    topic_name=models.CharField(verbose_name='主题内容',max_length=30,)
    is_default=models.BooleanField(verbose_name='是否是默认主题',default=False)
    is_delete=models.BooleanField(verbose_name='是否删除',default=False)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')

    def __str__(self):
        '''这是返回的描述信息'''
        return self.topic_name
    
    def get_count(self):
        '''这是统计每个主题写有多少篇未删除的博客的方法'''
        blog_num=self.blog_set.filter(is_delete=False).count()
        return blog_num

    class Meta:
        '''这是元信息类'''
        verbose_name='主题信息'
        verbose_name_plural=verbose_name

class Blog(models.Model):
    '''这是博客的模型类'''
    author=models.ForeignKey(UserProfile,verbose_name='博主',on_delete=models.CASCADE)
    blog_title=models.CharField(verbose_name='博客标题',max_length=40)
    blog_text=models.TextField(verbose_name='博客正文')
    category=models.CharField(choices=(('lr','文学'),('art','艺术'),('emo','情感'),('tech','科技'),('hth','健康'),('bt','美妆'),('oth','其他')),verbose_name='博客分类',max_length=5)
    blog_topic=models.ForeignKey(Topic,verbose_name='博客主题',on_delete=models.CASCADE)
    is_delete=models.BooleanField(verbose_name='是否删除',default=False)
    click_num=models.IntegerField(verbose_name='点击量',default=0)
    thumb_num=models.IntegerField(verbose_name='点赞数',default=0)
    comment_num=models.IntegerField(verbose_name='评论数',default=0)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')
    
    def __str__(self):
        '''这是返回的描述'''
        return self.blog_title

    class Meta:
        '''这是元信息类'''
        verbose_name='博客信息'
        verbose_name_plural=verbose_name

class CollectBookMark(models.Model):
    '''这是收藏夹的模型类'''
    owner=models.ForeignKey(UserProfile,verbose_name='收藏夹拥有者',on_delete=models.CASCADE)
    bookmark_name=models.CharField(max_length=30,verbose_name='收藏夹名字')
    is_default=models.BooleanField(verbose_name='是否是默认收藏夹',default=False)
    is_delete=models.BooleanField(verbose_name='是否删除',default=False)
    addtime=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')
    
    def __str__(self):
        '''这是返回的描述'''
        return self.bookmark_name

    class Meta:
        '''这是元信息类'''
        verbose_name='收藏夹信息'
        verbose_name_plural=verbose_name