$(document).ready(function() {
    let companies_locations_json = JSON.parse(companies_locations);
    console.log(companies_locations_json);
    
    var madrid = new google.maps.LatLng(40.5248319, -3.771562775451811);
    var map = new google.maps.Map(document.getElementById('map'), {
        center: madrid,
        zoom: 7,
        mapTypeId: 'roadmap'
    });
    
    var heatmapData = [];
    
    for (loc in companies_locations_json) {
        //let loc = "Toledo"
        let url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + companies_locations_json[loc]._id + "&region=es&key=";
        fetch(url)
        .then(response => response.json())
        .then(data => {
            for(var i = 0; i < companies_locations_json[loc].count; i++) {
                heatmapData.push(new google.maps.LatLng(
                    parseInt(data.results[0].geometry.location.lat), 
                    parseInt(data.results[0].geometry.location.lng)
                ))
            }
            
            var heatmap = new google.maps.visualization.HeatmapLayer({
                data: heatmapData
            });
            heatmap.setMap(map); 
        })
        .catch(function(error) {
            console.log('Hubo un problema con la petición Fetch:' + error.message);
        });
    }
    
});
