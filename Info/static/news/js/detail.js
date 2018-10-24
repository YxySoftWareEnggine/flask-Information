function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        var params = {
            "news_id" : $(this).attr("data-newid"),
            "action":"collect"
        };
        $.ajax({
            url:"/news/news_collect",
            method:"POST",
            contentType: "application/json",
            headers:{
                "X-CSRFToken":getCookie('csrf_token')
            },
            data:JSON.stringify(params),
            dataType: "json",
            success:function (resp) {
                if (resp.errno == "0")
                {
                    $(".collected").show();
                    $(".collection").hide();
                }
                else if (resp.errno == "4101") {
                    $(".login_form_con").show();
                }
                else {
                    alert(resp.errmsg);
                }
            }
        })
    });

    // 取消收藏
    $(".collected").click(function () {
        var params = {
            "news_id" : $(this).attr("data-newid"),
            "action":"cancel_collect"
        }
        $.ajax({
            url:"/news/news_collect",
            type:"POST",
            contentType: "application/json",
            headers:{
                "X-CSRFToken":getCookie('csrf_token')
            },
            data:JSON.stringify(params),
            success:function (resp) {
                if (resp.errno == "0") {
                    $(".collected").hide();
                    $(".collection").show();
                }
                else if (resp.errno == "4101")
                {
                    $(".login_form_con").show();
                }
                else {
                    alert(resp.errmsg);
                }
            }
        })
     
    })

        // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var params = {
             "news_id" : $(".collected").attr("data-newid"),
             "comment" : $(".comment_input").val()
        };
        if(!params.comment){
            alert("请输入评论内容");
            return
        }

        $.ajax({
            url:"/news/news_comment",
            type:"POST",
            contentType: "application/json",
            headers:{
                "X-CSRFToken":getCookie('csrf_token')
            },
            data:JSON.stringify(params),
            success:function (resp) {
                if (resp.errno == "0") {
                    var comments = resp.data;
                    if (comments.user.avatar_url == null)
                    {
                        comments.user.avatar_url = ""
                    }
                    var comment_html = ''
                    comment_html += '<div class="comment_list">'
                    comment_html += '<div class="person_pic fl">'
                    comment_html += '<img src="' + comments.user.avatar_url + '" alt="用户图标">'
                    comment_html += '</div>'
                    comment_html += '<div class="user_name fl">' + comments.user.nick_name + '</div>'
                    comment_html += '<div class="comment_text fl">'
                    comment_html += comments.content
                    comment_html += '</div>'
                    comment_html += '<div class="comment_time fl">' + comments.create_time + '</div>'

                    comment_html += '<a href="javascript:;" class="comment_up fr" comment_id="' + comments.id + '" news_id="' + comments.news_id + '">赞</a>'
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                    comment_html += '<form class="reply_form fl" data-commendid="' + comments.id + '" data-newsid="' + comments.news_id + '">'
                    comment_html += '<textarea class="reply_input"></textarea>'
                    comment_html += '<input type="button" value="回复" class="reply_sub fr">'
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                    comment_html += '</form>'

                    comment_html += '</div>'
                    $(".comment_list_con").prepend(comment_html)
                    $('.comment_sub').blur();

                    // 清空输入框内容
                    $(".comment_input").val("")
                }
                else if (resp.errno == "4101")
                {
                    $(".login_form_con").show();
                }
                else {
                    alert(resp.errmsg);
                }
            }
        })

    })

    $('.comment_list_con').delegate('a,input','click',function(){

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
            var $this = $(this);
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up')
            }else {
                $this.addClass('has_comment_up')
            }
        }

        if (sHandler.indexOf('reply_sub') < 0) {
        } else {
            var $this = $(this)
            var news_id = $this.parent().attr('data-newsid');
            var parent_id = $this.parent().attr('data-commentid');
            var news_comment = $this.prev().val();

            if (!news_comment) {
                alert('请输入评论内容');
                return
            }

            var params = {
                "news_id": news_id,
                "news_comment": news_comment,
                "parent_id": parent_id
            }
            $.ajax({
                url:"/news/news_comment",
                type:"post",
                contentType:"application/json",
                headers:{
                    "X-CSRFToken":getCookie("csrf_token")
                },
                data:JSON.stringify(params),
                success:function (resp) {
                    if(resp.errno=="0")
                    {
                        
                    }

                }
            })

        }
    })

    // 关注当前新闻作者
    $(".focus").click(function () {

    })

    // 取消关注当前新闻作者
    $(".focused").click(function () {

    })
})