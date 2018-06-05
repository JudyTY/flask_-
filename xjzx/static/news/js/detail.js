function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){
    get_comments();
    vue_comment_list = new Vue({
        el:'.comment_list_con',
        data:{
            comment_list:[]
        },
        delimiters:['[[',']]']
    });
    // 收藏
    $(".collection").click(function () {
        $.post('/collect',{'news_id':$('#news_id'
        ).val(),'csrf_token':$("#csrf_token").val()},function (data) {
            if(data.login){
                $('.login_btn').click()
            }
            else if(data.error_info){
                alert(data.error_info)
            }
            else if(data.success_info){
                $('.collection').hide();
                $('.collected').show();
            }
        })
       
    });

    // 取消收藏
    $(".collected").click(function () {
        $.post('/collect',{'news_id':$('#news_id'
        ).val(),'csrf_token':$("#csrf_token").val(),'action':1},function (data) {
            if(data.error_info){
                alert(data.error_info)
            }
            else if(data.success_info) {
                $('.collection').show();
                $('.collected').hide();
            }
        })
    });

    // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        $.post('/comment',{'news_id':$('#news_id'
        ).val(),'csrf_token':$("#csrf_token").val(),'msg':$('.comment_input').val()},function (data) {
            if(data.error_info){
                alert(data.error_info)
            }
            else if(data.success_info){
                $('.comment_input').val('');
                get_comments();
            }
        })

    });

    $('.comment_list_con').delegate('a,input','click',function(){
        $this = $(this);
        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {

            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            // var $this = $(this);
            var action=1;
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞

                action=''
            }else {

                action=1
            }

                $.post('/comment/up',{
                    'csrf_token':$('#csrf_token').val(),
                    'comment_id':$this.attr('comment_id'),
                    'action':action
                },function (data) {
                    if(data.login){
                        $('.login_btn').click()
                    }
                    else if(data.success_info){
                        $this.children().text(data.like_count);
                        if(action==1){
                            $this.addClass('has_comment_up');
                        }
                        else {
                            $this.removeClass('has_comment_up');
                        }

                    }
                }
                )
        }

        if(sHandler.indexOf('reply_sub')>=0)
        {
            $.post('/comment/reply',
                {
                'news_id':$('#news_id').val(),
                'comment_id':$this.attr("comment_id"),
                'csrf_token':$('#csrf_token').val(),
                'msg':$this.prev().val()
                },
                function (data) {
                    if(data.login){
                        $('.login_btn').click()
                    }
                    else if(data.success_info){
                        $this.prev().val('');
                        $this.parent().toggle();
                        get_comments();
                    }
            })
        }
    });

    // 关注当前新闻作者
    $(".focus").click(function () {
        $.post('/follow',{
            'csrf_token':$('#csrf_token').val(),
            'action':1,
            'follow_user_id':$('#news_user_id').val()
        },function(data) {
            if(data.login){
                $('.login_btn').click()
            }
            if(data.success_info){
                $('.focus').hide();
                $('.focused').show();
                $('.follows>b').text(parseInt($('.follows>b').text())+1)
            }
        })
    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {
        $.post('/follow',{
            'csrf_token':$('#csrf_token').val(),
            'action':2,
            'follow_user_id':$('#news_user_id').val()
        },function(data) {
            if(data.success_info){
                $('.focus').show();
                $('.focused').hide();
                $('.follows>b').text(parseInt($('.follows>b').text())-1)
            }
        })

});
});
function get_comments(){
    $.get('/comment',{'news_id':$('#news_id'
        ).val()},function (data) {
        vue_comment_list.comment_list=data.comment_list;
        $('#comment_count').text(data.comment_count);
        $('.comment_count>span').text(data.comment_count);;
    });
}