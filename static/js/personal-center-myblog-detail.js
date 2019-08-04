$(document).ready(function(){
    $('.comment p').hover(function(){
        $(this).find('.reply').css('display','inline');
        $(this).find('.delete-c').css('display','inline');
    },function(){
        $(this).find('.reply').css('display','none');
        $(this).find('.delete-c').css('display','none');
    })

})