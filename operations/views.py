from django.shortcuts import render
from django.views import View
from .models import UserThumbup,UserFollow
from users.models import UserProfile
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

class FollowView(View):
    '''这是处理关注和取消关注的视图'''
    def get(self,request):
        idol_id=request.GET.get('idol_id','')
        #如果关注人的id传过来了,先看看关注表里有没有该用户关注该博主的记录
        if idol_id:
            userfollow_list=UserFollow.objects.filter(oneself=request.user,idol_id=int(idol_id))
            idol=UserProfile.objects.filter(id=int(idol_id))[0]
            #如果有记录，看看现在是关注还是没关注的状态
            if userfollow_list:
                userfollow=userfollow_list[0]
                #如果是关注的状态，那么就是要取关。要记得把该用户的关注人减少一个，该博主的粉丝减少一个
                if userfollow.fstatus:
                    userfollow.fstatus=False
                    #看看以前是不是互关状态，如果是互关状态，要把两条关注记录的互关都取消
                    if userfollow.is_mutual:
                        userfollow.is_mutual=False
                        #这是另一条从博主角度出发的关注记录
                        reversefollow=UserFollow.objects.filter(oneself=idol,idol_id=request.user.id)[0]
                        reversefollow.is_mutual=False
                        reversefollow.save()
                    userfollow.save()
                    request.user.follow_num-=1
                    request.user.save()
                    idol.fan_num-=1
                    idol.save()
                    if userfollow.is_mutual:
                        is_mutual=1
                    else:
                        is_mutual=0

                    return JsonResponse({'status':'ok','msg':'关注','is_mutual':is_mutual,'num':-1})
                #如果现在是没有关注的状态，那么就是要恢复关注。记得该用户的关注人加一，该博主的粉丝加一。
                else:
                    userfollow.fstatus=True
                    #看看博主关没关注访问者，如果关注了，就要把两条记录都改成互关
                    reversefollow_list=UserFollow.objects.filter(oneself=idol,idol_id=request.user.id,fstatus=True)
                    if reversefollow_list:
                        reversefollow=reversefollow_list[0]
                        reversefollow.is_mutual=True
                        reversefollow.save()
                        userfollow.is_mutual=True
                    userfollow.save()
                    request.user.follow_num+=1
                    request.user.save()
                    idol.fan_num+=1
                    idol.save()
                    if userfollow.is_mutual:
                        is_mutual=1
                    else:
                        is_mutual=0
                    return JsonResponse({'status':'ok','msg':'取消关注','is_mutual':is_mutual,'num':1})
            #如果没有记录，那就要新建一条关注记录，并且该用户关注人加一，该博主粉丝加一
            else:
                new_userfollow=UserFollow()
                new_userfollow.oneself=request.user
                new_userfollow.idol_id=int(idol_id)
                new_userfollow.fstatus=True
                #看看博主关没关注访问者，如果关注了，就要把两条关注记录都改成互关
                reversefollow_list=UserFollow.objects.filter(oneself=idol,idol_id=request.user.id)
                if reversefollow_list:
                    reversefollow=reversefollow_list[0]
                    reversefollow.is_mutual=True
                    reversefollow.save()
                    new_userfollow.is_mutual=True
                new_userfollow.save()
                request.user.follow_num+=1
                request.user.save()
                idol.fan_num+=1
                idol.save()
                if new_userfollow.is_mutual:
                    is_mutual=1
                else:
                    is_mutual=0
                return JsonResponse({'status':'ok','msg':'取消关注','is_mutual':is_mutual,'num':1})
        #如果id没有传过来
        else:
            return JsonResponse({'status':'fail','msg':'操作失败'})


