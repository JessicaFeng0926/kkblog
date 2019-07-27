$(document).ready(function(){
	
	//下面是鼠标在博客标题上方悬停和结束悬停的事件，悬停就出现移动和删除按钮，离开就隐藏
	var blog_title=$('.blog-title');
	blog_title.hover(function(){
		var edit=$(this).children('.edit');
		var delete_btn=$(this).children('.delete-btn');
		edit.css('display','inline');
		delete_btn.css('display','inline');
	},function(){
		var edit=$(this).children('.edit');
		var delete_btn=$(this).children('.delete-btn');
		edit.css('display','none');
		delete_btn.css('display','none');
	})
	
})
