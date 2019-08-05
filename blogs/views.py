from django.shortcuts import render,redirect,reverse
from django.views import View
from .models import Topic,Blog,CollectBookMark
from users.models import UserProfile
from operations.models import UserFollow,UserThumbup,UserCollect,UserComment
from django.http import JsonResponse
from users.views import get_data_list
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from tools.decorator import login_decorator
# Create your views here.

class DeleteTopicView(View):
    '''这是删除主题的视图类'''
    def get(self,request):
        topic_id=request.GET.get('topic_id','')
        if topic_id:
            topic_list=Topic.objects.filter(id=topic_id)
            if topic_list:
                topic=topic_list[0]
                topic.is_delete=True
                topic.save()
                return JsonResponse({'status':'ok','msg':'主题删除成功'})
            else:
                return JsonResponse({'status':'fail','msg':'主题删除失败'})
        else:
            return JsonResponse({'status':'fail','msg':'主题删除失败'})

class DeleteBlogView(View):
    '''这是删除博客的视图类'''
    def get(self,request):
        blog_id=request.GET.get('blog_id','')
        print(blog_id)
        if blog_id:
            blog_list=Blog.objects.filter(id=int(blog_id))
            if blog_list:
                blog=blog_list[0]
                blog.is_delete=True
                blog.save()
                #如果一篇博客被删除了，那么作者的总阅读量也要减去该博客的阅读量
                blog.author.visit_num-=blog.click_num
                blog.author.save()
                return JsonResponse({'status':'ok','msg':'博客删除成功'})
            else:
                return JsonResponse({'status':'fail','msg':'博客删除失败'})
        else:
            return JsonResponse({'status':'fail','msg':'博客删除失败'})


class BlogListView(View):
    '''这是某位博主的所有博客列表页的视图类'''
    @login_decorator
    def get(self,request,author_id):
        if author_id:
            #判断访问者和要访问的博主是否是统一个人
            #如果是同一个人，就重定向到自己的个人中心
            if request.user.id==int(author_id):
                return redirect(reverse('users:pc'))
            #如果不是同一个人，就到该博主的列表页
            else:
                #看看博主存不存在
                author_list=UserProfile.objects.filter(id=int(author_id))
                if author_list:
                    #找到该博主
                    author=UserProfile.objects.filter(id=int(author_id))[0]
                    #找到该博主的全部分类，全部时间归档，全部主题
                    data_list=get_data_list(author)
                    topic_list=data_list[0]
                    blog_list=data_list[1]
                    time_list=data_list[2]
                    #查看访问者对每篇博客的收藏状态，并添加到每篇博客的对象里
                    for blog in blog_list:
                        usercollect_list=UserCollect.objects.filter(collector=request.user,collect_blog=blog,cstatus=True)
                        if usercollect_list:
                            blog.cstatus=True
                        else:
                            blog.cstatus=False
                            
                    #查询访问者是否关注了该博主
                    fstatus=False
                    is_mutual=False
                    userfollow_list=UserFollow.objects.filter(oneself=request.user,idol_id=int(author_id),fstatus=True)
                    if userfollow_list:
                        fstatus=True
                        #如果访问者关注了该博主，再查询一下是否互相关注了
                        userfollow=userfollow_list[0]
                        if userfollow.is_mutual:
                            is_mutual=True
                    #如果访问者点击了某个主题，就要进一步筛选博客
                    topic_id=request.GET.get('topic','')
                    if topic_id:
                        topic_id=int(topic_id)
                        blog_list=blog_list.filter(blog_topic_id=topic_id).order_by('-addtime')
                    #如果访问者点击了某个月份，就要按照年月进一步筛选博客
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
                    return render(request,'blogs/blogs-list.html',{'author':author,'topic_list':topic_list,'time_list':time_list,'fstatus':fstatus,'is_mutual':is_mutual,'topic_id':topic_id,'year':year,'month':month,'current_page':current_page})
                else:
                    return redirect(reverse('index'))


class BlogDetailView(View):
    '''这是博客详情页的视图类'''
    @login_decorator
    def get(self,request,blog_id):
        if blog_id:
            blog_list=Blog.objects.filter(id=int(blog_id),is_delete=False)
            if blog_list:
                blog=blog_list[0]
                #如果访问者和博主是一个人，那就重定向到博主的个人详情页
                if request.user==blog.author:
                    return redirect(reverse('users:myblog_detail',args=[blog.id]))
                else:
                    #不是一个人，就到那位博主的这篇博客的阅读页
                    #要给这篇博客的阅读量加1，作者的访问量也加1
                    blog.click_num+=1
                    blog.save()
                    blog.author.visit_num+=1
                    blog.author.save()

                    #查找访问者对这篇博客的点赞状态
                    tstatus=False
                    userthumb_list=UserThumbup.objects.filter(oneself=request.user,thumbup_blog=blog,tstatus=True)
                    if userthumb_list:
                        tstatus=True
                    
                    #查找访问者对这位博主的关注状态,两个人的互关状态
                    fstatus=False
                    is_mutual=False
                    userfollow_list=UserFollow.objects.filter(oneself=request.user,idol_id=blog.author.id,fstatus=True)
                    if userfollow_list:
                        fstatus=True
                        is_mutual=userfollow_list[0].is_mutual

                    #查找访问者对这篇博客的收藏状态
                    cstatus=False
                    usercollect_list=UserCollect.objects.filter(collector=request.user,collect_blog=blog,cstatus=True)
                    if usercollect_list:
                        cstatus=True

                    #查找这个博主的全部主题和全部月份归档
                    data_list=get_data_list(blog.author)
                    topic_list=data_list[0]
                    time_list=data_list[2]

                    #查看本篇博客的所有评论
                    usercomment_list=UserComment.objects.filter(comment_blog=blog,is_delete=False).order_by('-addtime')
                    for usercomment in usercomment_list:
                        usercomment.listener=UserProfile.objects.filter(id=usercomment.listener_id)[0]

                    return render(request,'blogs/blog-detail.html',{'blog':blog,'topic_list':topic_list,'time_list':time_list,'tstatus':tstatus,'fstatus':fstatus,'is_mutual':is_mutual,'cstatus':cstatus,'usercomment_list':usercomment_list})
            else:
                return redirect(reverse('index'))

class DeleteBookmarkView(View):
    '''这是删除收藏夹的视图类'''
    def get(self,request):
        bookmark_id=request.GET.get('bookmark_id','')
        if bookmark_id:
            bookmark_list=CollectBookMark.objects.filter(id=int(bookmark_id))
            if bookmark_list:
                bookmark=bookmark_list[0]
                bookmark.is_delete=True
                bookmark.save()
                return JsonResponse({'status':'ok','msg':'收藏夹删除成功'})
            else:
                return JsonResponse({'status':'fail','msg':'收藏夹删除失败'})
        else:
            return JsonResponse({'status':'fail','msg':'收藏夹删除失败'})  

