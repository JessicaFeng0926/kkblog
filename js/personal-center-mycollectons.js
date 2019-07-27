$(document).ready(function(){
	
	//下面是鼠标在博客标题上方悬停和结束悬停的事件，悬停就出现移动和删除按钮，离开就隐藏
	var blog_title=$('.blog-title');
	blog_title.hover(function(){
		var move=$(this).children('.move');
		var delete_cl=$(this).children('.delete-cl');
		move.css('display','inline');
		delete_cl.css('display','inline');
	},function(){
		var move=$(this).children('.move');
		var delete_cl=$(this).children('.delete-cl');
		move.css('display','none');
		delete_cl.css('display','none');
	})
	
})
