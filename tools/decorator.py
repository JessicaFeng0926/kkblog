from django.shortcuts import redirect,reverse
from django.http import JsonResponse

def login_decorator(func):
    '''这是一个登录装饰器，它会阻止未登录的用户做一些事情'''
    def inner(self,request,*args,**kwargs):
        #如果登录了，就按照原计划走
        if request.user.is_authenticated:
            return func(self,request,*args,*kwargs)
        #没登录，要处理ajax请求和普通请求
        else:
            if request.is_ajax():
                return JsonResponse({'status':'nologin','msg':'请登录后再操作'})
            #获取当前的url
            url=request.get_full_path()
            #把url存在登录页面的cookie里面
            ret=redirect(reverse('users:login'))
            ret.set_cookie('url',url)
            return ret
    return inner

        