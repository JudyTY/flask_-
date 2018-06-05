function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".pic_info").submit(function (e) {
        e.preventDefault();
        // 图片的上传需要用到ajaxSubmit方法
        $(this).ajaxSubmit({
        url: "/user/pic",
        type: "post",
        dataType: "json",
        success: function (data) {
            if (data.success_info) {
                $('.now_user_pic').attr('src',data.avatar_url);
                $('#user_avatar',parent.document).attr('src',data.avatar_url);
                $('.lgin_pic',parent.document).attr('src',data.avatar_url);

            }
            else if(data.error_info){
                alert(data.error_info);
            }
        }
    });

    });

});