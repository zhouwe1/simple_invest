

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
        }, 100)
        newTbody.find('input:first').focus()
    }
});
