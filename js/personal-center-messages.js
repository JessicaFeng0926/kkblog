$(document).ready(function(){
	var msg_title=$('.msg-title');
	msg_title.hover(function(){
		var delete_msg=$(this).children('.delete-msg');
		delete_msg.css('display','inline')
		
	},function(){
		var delete_msg=$(this).children('.delete-msg');
		delete_msg.css('display','none')
	})
	
})
