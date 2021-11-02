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
    /* Data points defined as an array of LatLng objects */
    var heatmapData = [
        new google.maps.LatLng(37.782, -122.447),
        new google.maps.LatLng(37.782, -122.445),
        new google.maps.LatLng(37.782, -122.443),
        new google.maps.LatLng(37.782, -122.441),
        new google.maps.LatLng(37.782, -122.439),
        new google.maps.LatLng(37.782, -122.437),
        new google.maps.LatLng(37.782, -122.435),
        new google.maps.LatLng(37.785, -122.447),
        new google.maps.LatLng(37.785, -122.445),
        new google.maps.LatLng(37.785, -122.443),
        new google.maps.LatLng(37.785, -122.441),
        new google.maps.LatLng(37.785, -122.439),
        new google.maps.LatLng(37.785, -122.437),
        new google.maps.LatLng(37.785, -122.435)
    ];

    var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);

    var map = new google.maps.Map(document.getElementById('map'), {
        center: sanFrancisco,
        zoom: 13,
        mapTypeId: 'satellite'
    });

    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData
    });
    heatmap.setMap(map); 
    
    $('.close-flash').on('click', close_flash_messages);
});
