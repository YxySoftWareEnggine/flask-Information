function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".focused").click(function () {
        // TODO 取消关注当前新闻作者
        var follow = false;
        var cid = $(this).attr('data-author');
        var params = {
            "follow": follow,
            "cid": cid
        };
        $.ajax({
            url: "/user/news_Canle_follow",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    window.location.reload()
                }
                else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})