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
            $.growl.notice({title: '已退出Todo模式', message: '请等待页面刷新', location:"tr"});
            setTimeout(function(){
                location.reload()
            }, 1000);
        }
        else{
            let today = moment().format("YYYY-MM-DD");
            $('#dataTbody').attr('data-todo', 'on');
            $(this).addClass('btn-primary');
            $(this).removeClass('btn-default');
            $.growl.notice({title: 'Todo模式开启', message: '今天内更新过的记录都会被隐藏，只留下待更新的记录', location:"tr"});
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

    })
});



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