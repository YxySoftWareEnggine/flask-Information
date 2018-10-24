function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pass_info").submit(function (e) {
        e.preventDefault();

        // TODO 修改密码
        if($('#New').val() == $('#ConfimNew').val())
        {

            var params={
               "CurrentPass":$('#CurrentPass').val(),
                "NewPass":$('#New').val(),
                "ConfimNew":$('#ConfimNew').val()
            };
           $.ajax({
                url:"/user/pass_info",
                type:"post",
                contentType:"application/json",
                headers:{
                    "X-CSRFToken":getCookie("csrf_token")
                },
                data:JSON.stringify(params),
                success:function (resp) {
                    if(resp.errno=="0")
                    {
                       alert('保存成功');
                    }
                    else
                    {
                        alert(resp.errmsg);
                    }

                }
            })
        }
        else
        {
            alert("两次密码输入不一致");
        }
    })
})