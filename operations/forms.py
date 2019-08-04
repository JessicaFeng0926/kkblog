from django import forms

class NewCommentForm(forms.Form):
    '''这是验证用户评论的表单类'''
    lid=forms.IntegerField(required=False)
    comment_blog_id=forms.IntegerField()
    comment_content=forms.CharField(required=True,max_length=100,
    error_messages={
        'required':'评论内容不能为空',
        'max_length':'评论字数不能超过100'
    })