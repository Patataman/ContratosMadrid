function close_flash_messages() {
    var container = $(this).parent().parent();
    $(this).parent().remove();

    if ($(container).children().length == 0){
        $(container).parent().remove();
    }
}

function generate_messages(msg, type) {
    html = '<div class="col-12 pl-5 flash '+type+'">' +
           '<ul class="m-0 col-12 p-0">' +
           '<li>'+msg+'<i class="float-right close-flash fa fa-times mt-1"></i></li></ul></div>';
    $(html).insertBefore("#content");
    $('.close-flash').on('click', close_flash_messages);
}


$(document).ready(function() {
    $('.close-flash').on('click', close_flash_messages);
});
