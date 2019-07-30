from django.shortcuts import render
from django.views import View
from .models import UserThumbup
from django.http import JsonResponse

# Create your views here.

class ThumbupView(View):
    '''这是处理点赞和取消点赞的视图类'''
    def get(self,request):
        blog_id=request.GET.get('blog_id','')
        if blog_id:
            user_thumbup_list=UserThumbup.objects.filter(oneself=request.user,thumbup_blog_id=int(blog_id))
            #看看该用户以前给没给这篇博文点过赞，如果点过就看看现在是赞的状态还是非赞的状态
            if user_thumbup_list:
                user_thumbup=user_thumbup_list[0]
                #如果现在是赞的状态，那么用户现在想做的就是取消点赞,同时要减少本篇博客的点赞和博主的赞
                if user_thumbup.tstatus:
                    user_thumbup.tstatus=False
                    user_thumbup.save()
                    user_thumbup.thumbup_blog.thumb_num-=1
                    user_thumbup.thumbup_blog.save()
                    user_thumbup.thumbup_blog.author.thumb_num-=1
                    user_thumbup.thumbup_blog.author.save()
                    return JsonResponse({'status':'ok','msg':'black','num':-1})
                #如果现在是没有赞的状态，那么用户现在想做的就是恢复点赞，同时要加上博客和博主的赞
                else:
                    user_thumbup.tstatus=True
                    user_thumbup.save()
                    user_thumbup.thumbup_blog.thumb_num+=1
                    user_thumbup.thumbup_blog.save()
                    user_thumbup.thumbup_blog.author.thumb_num+=1
                    user_thumbup.thumbup_blog.author.save()
                    return JsonResponse({'status':'ok','msg':'red','num':1})
            #从来没有点过赞，就要创建一条新的点赞数据,完成点赞，加上博客和博主的赞
            else:
                new_user_thumbup=UserThumbup()
                new_user_thumbup.oneself=request.user
                new_user_thumbup.thumbup_blog_id=blog_id
                new_user_thumbup.tstatus=True
                new_user_thumbup.save()
                new_user_thumbup.thumbup_blog.thumb_num+=1
                new_user_thumbup.thumbup_blog.save()
                new_user_thumbup.thumbup_blog.author.thumb_num+=1
                new_user_thumbup.thumbup_blog.author.save()
                return JsonResponse({'status':'ok','msg':'red','num':1})
        #没有传过来id，就点赞失败
        else:
            return JsonResponse({'status':'fail','msg':'操作失败'})



