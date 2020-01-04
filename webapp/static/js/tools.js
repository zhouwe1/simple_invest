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