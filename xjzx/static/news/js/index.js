var currentCid = 0; // 当前分类 id
var cur_page = 1; // 当前页
// var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据
var clickCid=0;  // 默认最新页


$(function () {
    index_data = new Vue({
        // 接管新闻列表
        el:'.list_con',
        delimiters: ['[[', ']]'],
        data:{
            news_list:[]
        }
    });
    // 首页分类切换
    $('.menu li').click(function () {
        clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        $(this).addClass('active');

        if (clickCid != currentCid) {
            // 切换分类时,默认请求第一页
            cur_page=1;
            updateNewsData();
            // TODO 去加载新闻数据
            // 将当前页置为此页,再进行换页时能正常执行此函数
            currentCid=clickCid;

        }
    });

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            // 滚动之后即加载下一页
            cur_page+=1;
            // 请求数据状态为真,则去请求数据
            if(data_querying==true){
                updateNewsData();
            }

        }
    })
});

function updateNewsData() {
    // TODO 更新新闻数据

    // 当执行到此函数,就将请求状态赋值为false,就不会重复请求同一个页面
    data_querying = false;
    $.get('/index_data',{'page':cur_page,'category_id':clickCid},function (data) {
        if(cur_page==1){
        // 如果请求页数是第一页,即只显示4条数据,只赋值不拼接
        index_data.news_list = data.news_list;
        // 第一页请求结束后,需要获取下一页,将请求状态置为真
        data_querying = true;
        }
        else {
            // concat用来合并两个数组,返回一个合并后的结果
            index_data.news_list = index_data.news_list.concat(data.news_list);
            // // 将从服务器获得的当前页码赋值给全局变量cur_page
            cur_page = data.page;
            // 当本页数据请求结束,将请求状态赋值为真,可以继续请求下一页面
            data_querying = true;
        }
    })


};
// 显示页面时默认加载四条数据
updateNewsData();
