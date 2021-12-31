$(function () {
    refresh_sidebar();
    load_avatar(user_avatar);

    $('.tr-clone').click(function () {
        let clone_tr = $('#dataTbody .clone-tr');

        if (clone_tr.length > 0){
            clone_tr.addClass('tr-error');
            setTimeout(function(){
                clone_tr.removeClass('tr-error')
            }, 100)
        }
        else{
            $('#dataTbody').prepend($('#cloneTbody > tr').clone())
        }
    });

    $('.tr-add').click(function () {
        let newTbody = $('#newTbody');
        if(newTbody.hasClass('d-none')){
            newTbody.removeClass('d-none');
            newTbody.find('input:first').focus()
        }
        else{
            newTbody.children('tr').addClass('tr-error');
            setTimeout(function(){
                newTbody.children('tr').removeClass('tr-error')
            }, 100);
            newTbody.find('input:first').focus()
        }
    });

    $('.tr-todo').click(function () {
        let todo_mode = $('#dataTbody').attr('data-todo');
        if(todo_mode=='on'){
            swalSuccess('已退出Todo模式，请等待页面刷新');
            setTimeout(function(){
                location.reload()
            }, 1000);
        }
        else{
            let today = moment().format("YYYY-MM-DD");
            $('#dataTbody').attr('data-todo', 'on');
            $(this).addClass('btn-primary');
            $(this).removeClass('btn-default');
            swalInfo('Todo模式开启，今天内更新过的记录都会被隐藏，只留下待更新的记录');
            $('#dataTbody tr').each(function () {
                let tr_date = $(this).attr('data-update_time'),
                    tr = $(this);
                if(moment(tr_date).isAfter(today)){
                    tr.addClass('tr-success');
                    setInterval(function () {
                        tr.remove()
                    }, 1000);
                }
            })
        }

    });

    $('.dashboard-pie-view-detail').click(function () {
        window.location.href='/analyse/scale'
    })
});

let Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000
    });

let pieOptions = {
        maintainAspectRatio : false,
        responsive : true,
        legend: {position: 'right'}
    },
    areaChartOptions = {
        maintainAspectRatio : false,
        responsive : true,
        legend: {display: false},
        scales: {
            xAxes: [{
                gridLines : {display : false}
            }],
            yAxes: [{
                gridLines : {display : false}
            }]
        }
    };

function load_avatar(url) {
    $('#nav-user-avatar').prepend('<img alt src="'+ url +'" class="user-image img-circle elevation-2">');
    $('.user-header').prepend('<img src="'+ url +'" class="img-circle elevation-2" alt="User Image">')
}

function refresh_sidebar() {
    let current_path = window.location.pathname;
    $('.nav-sidebar a').each(function () {
        if(current_path==$(this).attr('href')){
            $(this).parents('li').children('a').addClass('active');
            $(this).parents('li.has-treeview').addClass('menu-open')
        }
    });
}

function fill_dashboard_agent_pie(labels, datas){
    //dashboard页面渠道占比
    let agentData = {
            labels: labels,
            datasets: [{
                data: datas,
                backgroundColor: ['#e75840','#a565ef','#628cee','#eb9358','#d05c7c','#bb60b2','#433e7c'],
            }]
        },
        pieChartCanvas = $('#agentChart').get(0).getContext('2d');
    new Chart(pieChartCanvas, {
        type: 'doughnut',
        data: agentData,
        options: pieOptions
    });
}

function fill_dashboard_fptype_pie(labels, datas){
    //dashboard页面类型占比
    let agentData = {
            labels: labels,
            datasets: [{
                data: datas,
                backgroundColor: ['#63b2ee', '#76da91', '#f8cb7f', '#f89588','#7cd6cf','#9192ab','#7898e1','#efa666','#eddd86','#9987ce','#63b2ee','#76da91'],
            }]
        },
        pieChartCanvas = $('#fptypeChart').get(0).getContext('2d');
    new Chart(pieChartCanvas, {
        type: 'doughnut',
        data: agentData,
        options: pieOptions
    });
}

function fill_trend_amount_chart(url) {
    //总额趋势图
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(r){
            let areaChartCanvas = $('#amountTrend').get(0).getContext('2d');
            let areaChartData = {
                labels  : r['labels'],
                datasets: [
                    {
                        backgroundColor     : "rgba(184,91,91,0.9)",
                        borderColor         : "rgba(184,91,91,0.8)",
                        pointBackgroundColor: "rgb(197,219,241)",
                        pointBorderColor    : "rgb(184,91,91)",
                        data                : r['differences'],
                        label               : "环比增长"
                    },
                    {
                        backgroundColor     : "rgba(60,141,188,0.9)",
                        borderColor         : "rgba(60,141,188,0.8)",
                        pointBackgroundColor: "rgb(197,219,241)",
                        pointBorderColor    : "rgb(1,84,114)",
                        data                : r['datas'],
                        label               : "金额"
                    },
                ]
            };
            areaChartOptions['legend'] = {display: true}
            new Chart(areaChartCanvas, {
                type: 'line',
                data: areaChartData,
                options: areaChartOptions
            })
        },
    })
}

function fill_trend_ua_chart(labels, datas) {
    //持仓理财产品趋势图
    $("html,body").animate({scrollTop:$("#uaTrend").offset().top},1000);
    let areaChartCanvas = document.getElementById("uaTrend").getContext('2d'),
        areaChartData = {
            labels  : labels,
            datasets: [
                {
                    backgroundColor     : 'rgba(60,141,188,0.9)',
                    borderColor         : 'rgba(60,141,188,0.8)',
                    pointBackgroundColor: "rgb(197,219,241)",
                    pointBorderColor    : "rgb(1,84,114)",
                    data                : datas,
                    label               : "金额"
                },
            ]
        };
    new Chart(areaChartCanvas, {
        type: 'line',
        data: areaChartData,
        options: areaChartOptions
    })
}

function swalError(msg) {Toast.fire({type: 'error', title: msg})}
function swalInfo(msg) {Toast.fire({type: 'info', title: msg})}
function swalSuccess(msg) {Toast.fire({type: 'success', title: msg})}
