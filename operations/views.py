from django.shortcuts import render,redirect,reverse
from django.views import View
from .models import UserThumbup,UserFollow,UserCollect,UserComment,UserNotice
from users.models import UserProfile
from blogs.models import CollectBookMark,Blog
from .forms import NewCommentForm
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

class CollectView(View):
    '''这是收藏的视图类'''
    def get(self,request):
        blog_id=request.GET.get('blog_id','')
        if blog_id:
            #看看有没有对这篇博客的收藏记录
            usercollect_list=UserCollect.objects.filter(collector=request.user,collect_blog_id=int(blog_id))
            #找到该用户的默认收藏夹
            bookmark=CollectBookMark.objects.filter(owner=request.user,is_default=True)[0]
            #如果有，就看看目前的收藏状态
            if usercollect_list:
                usercollect=usercollect_list[0]
                #如果目前是收藏状态，那现在就是想取消收藏
                if usercollect.cstatus:
                    usercollect.cstatus=False
                    usercollect.save()
                    return JsonResponse({'status':'ok','msg':'[收藏]'})
                #如果目前是未收藏的状态，那就是想重新收藏，重新收藏的还放回默认收藏夹
                else:
                    usercollect.cstatus=True
                    usercollect.bookmark=bookmark
                    usercollect.save()
                    return JsonResponse({'status':'ok','msg':'[取消收藏]'})
            #如果没有记录，就新建，并且收藏
            else:
                new_usercollect=UserCollect()
                new_usercollect.collector=request.user
                new_usercollect.collect_blog_id=int(blog_id)
                new_usercollect.cstatus=True
                new_usercollect.bookmark=bookmark
                new_usercollect.save()
                return JsonResponse({'status':'ok','msg':'[取消收藏]'})
        else:
            return JsonResponse({'status':'fail','msg':'操作失败'})

class MoveView(View):
    '''这是用户把收藏的博客移动收藏夹的视图类'''
    def post(self,request,usercollect_id):
        if usercollect_id:
            bookmark_id=request.POST.get('bookmark_id','')
            usercollect=UserCollect.objects.filter(id=int(usercollect_id))[0]
            usercollect.bookmark_id=int(bookmark_id)
            usercollect.save()
            return redirect(reverse('users:mycollections'))
        else:
            return redirect(reverse('users:mycollections'))

class ReadView(View):
    '''这是用户把消息标位已读的视图类'''
    def get(self,request):
        mid=request.GET.get('mid','')
        mtype=request.GET.get('mtype','')
        if mid and mtype:
            #如果是评论
            if mtype == 'c':
                usercomment=UserComment.objects.filter(id=int(mid))[0]
                #如果博主是我
                if usercomment.comment_blog.author == request.user:
                    #如果听话人也是我
                    if usercomment.listener_id == request.user.id:
                        usercomment.author_read=True
                        usercomment.listener_read=True
                    #如果听话人不是我
                    else:
                        usercomment.author_read=True
                #如果博主不是我
                else:
                    usercomment.listener_read=True
                usercomment.save()
            #如果是通知
            elif mtype == 'n':
                usernotice=UserNotice.objects.filter(id=int(mid))[0]
                usernotice.is_read=True
                usernotice.save()
            #如果是赞
            elif mtype == 't':
                userthumb=UserThumbup.objects.filter(id=int(mid))[0]
                userthumb.is_read=True
                userthumb.save()
            #如果是关注
            elif mtype == 'f':
                userfollow=UserFollow.objects.filter(id=int(mid))[0]
                userfollow.is_read=True
                userfollow.save()
            return JsonResponse({'status':'ok','msg':'消息标记成功'})
        else:
            return JsonResponse({'status':'fail','msg':'操作失败'})

class DeleteMsgView(View):
    '''这是删除消息的视图类'''
    def get(self,request):
        mid=request.GET.get('mid')
        mtype=request.GET.get('mtype')
        if mid and mtype:
            #如果是评论
            if mtype == 'c':
                usercomment=UserComment.objects.filter(id=int(mid))[0]
                #如果博主是我
                if usercomment.comment_blog.author == request.user:
                    #如果听话人也是我
                    if usercomment.listener_id == request.user.id:
                        usercomment.author_del = True
                        usercomment.listener_del = True
                    #如果听话人不是我
                    else:
                        usercomment.author_del=True
                #如果博主不是我
                else:
                    usercomment.listener_del=True
                usercomment.save()


            #如果是通知
            elif mtype == 'n':
                usernotice=UserNotice.objects.filter(id=int(mid))[0]
                usernotice.is_delete=True
                usernotice.save()
            #如果是点赞
            elif mtype == 't':
                userthumb=UserThumbup.objects.filter(id=int(mid))[0]
                userthumb.is_delete=True
                userthumb.save()
            #如果是关注
            elif mtype == 'f':
                userfollow=UserFollow.objects.filter(id=int(mid))[0]
                userfollow.is_delete=True
                userfollow.save()
            return JsonResponse({'status':'ok','msg':'消息删除成功'})
        else:
            return JsonResponse({'status':'fail','msg':'操作失败'})

class CommentView(View):
    '''这是用户评论的视图类'''
    def post(self,request):
        newcomment_form=NewCommentForm(request.POST)
        if newcomment_form.is_valid():
            lid=newcomment_form.cleaned_data['lid']
            comment_blog_id=newcomment_form.cleaned_data['comment_blog_id']
            comment_content=newcomment_form.cleaned_data['comment_content']
            if not lid:
                lid=Blog.objects.filter(id=int(comment_blog_id))[0].author_id
            newcomment=UserComment()
            newcomment.speaker=request.user
            newcomment.listener_id=lid
            newcomment.comment_blog_id=int(comment_blog_id)
            newcomment.comment_content=comment_content
            newcomment.save()
            #给博主的评论数加一
            newcomment.comment_blog.author.comment_num+=1
            newcomment.comment_blog.author.save()
            return JsonResponse({'status':'ok','msg':'评论成功'})

        else:
            error=''
            for k,v in newcomment_form.errors.items():
                error=error+v+','

            return JsonResponse({'status':'fail','msg':error})

class DeleteCommentView(View):
    '''这是博主删除评论的视图'''
    def get(self,request):
        cid=request.GET.get('cid','')
        if cid:
            usercomment=UserComment.objects.filter(id=int(cid))[0]
            usercomment.is_delete=True
            usercomment.save()
            #博主的评论数减一
            usercomment.comment_blog.author.comment_num-=1
            usercomment.comment_blog.author.save()
            return JsonResponse({'status':'ok','msg':'评论删除成功'})
        else:
            return JsonResponse({'status':'fail','msg':'评论删除失败'})