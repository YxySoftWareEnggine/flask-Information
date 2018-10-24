function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault();

        var params = {
            "signature":$("#signature").val(),
            "nick_name":$("#nick_name").val(),
            "gender":$(".gender").val()
        };

        if (!params.nick_name) {
            alert('请输入昵称');
            return
        }
        if (!params.gender) {
            alert('请选择性别');
        }

        // TODO 修改用户信息接口

        $.ajax({
            url:"/user/user_base_info",
            type:"post",
            contentType:"application/json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            data:JSON.stringify(params),
            success:function (resp) {
                if(resp.errno=="0")
                {
                        $('.user_center_name',parent.document).html(params["nick_name"]);
                        $('#nick_name',parent.document).html(params["nick_name"]);
                        $('.input_sub').blur();
                }
                else
                {
                    alert(resp.errmsg);
                }

            }
        })
    })
});