

$('.tr-add').click(function () {
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