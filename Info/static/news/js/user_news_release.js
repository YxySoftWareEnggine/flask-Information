function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault();
         $(this).ajaxSubmit({
            url: "/user/release_news",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    window.parent.fnChangeMenu(6);
                    window.parent.scrollTo(0, 0);
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})