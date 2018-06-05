function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {
    $(".base_info").submit(function (e) {
        e.preventDefault();
        var gender=$(".gender:checked").val();
        var signature = $("#signature").val();
        var nick_name = $("#nick_name").val();
        var csrf_token = $("#csrf_token").val();
        if (!nick_name) {
            alert('请输入昵称');
            return
        }
        if (!gender) {
            alert('请选择性别');
            return
        }
        $.post('/user/base',{'csrf_token':csrf_token,'signature':signature,"nick_name":nick_name,'gender':gender},function (data) {
            if(data.error_info){
                alert(data.error_info)}
            else{
            //  修改成功后更改主页面的昵称
                alert(data.success_info);
                $('#user_center_name',parent.document).text(nick_name);
                $('.user_center_name',parent.document).text(nick_name);
            }

        });
        // TODO 修改用户信息接口
    })
});