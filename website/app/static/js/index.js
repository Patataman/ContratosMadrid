$(document).ready(function() {
    var madrid = new google.maps.LatLng(40.5248319, -3.771562775451811);
    var map = new google.maps.Map(document.getElementById('map'), {
        center: madrid,
        zoom: 7,
        mapTypeId: 'roadmap'
    });

    var heatmapData = [];

    for (var i=0; i<companies_locations.length; i++) {
        heatmapData.push(new google.maps.LatLng(
            companies_locations[i].lat,
            companies_locations[i].lng
        ))
    }
    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatmapData
    });
    heatmap.setMap(map);
});
