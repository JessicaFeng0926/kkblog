from django.shortcuts import render,redirect,reverse
from django.views import View
from .models import Topic,Blog
from django.http import JsonResponse

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
                return JsonResponse({'status':'ok','msg':'博客删除成功'})
            else:
                return JsonResponse({'status':'fail','msg':'博客删除失败'})
        else:
            return JsonResponse({'status':'fail','msg':'博客删除失败'})


        