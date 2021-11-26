$(document).ready(function() {
    var madrid = new google.maps.LatLng(40.5248319, -3.771562775451811);
    var map = new google.maps.Map(document.getElementById('map'), {
        center: madrid,
        zoom: 7,
        mapTypeId: 'roadmap'
    });

    var max = Math.max.apply(null, companies_locations.flatMap(function(d) {return d.count}));
    var min = Math.max.apply(null, companies_locations.flatMap(function(d) {return d.count}));

    for (var i=0; i<companies_locations.length; i++) {
        const cityCircle = new google.maps.Circle({
          strokeColor: "#FF0000",
          strokeOpacity: 0.8,
          strokeWeight: 2,
          fillColor: "#FF0000",
          fillOpacity: 0.35,
          map,
          center: companies_locations[i].location,
          radius: Math.sqrt(companies_locations[i].count/max) * 100000,
        });
        new google.maps.Marker({
            position: companies_locations[i].location,
            map: map,
            icon: 'static/img/empty.png',
            label: {
                color: 'rgb(0,110,199)',
                fontWeight: 'bold',
                text: companies_locations[i].count + " contratos",
                fontSize: "1.8em",
            },
        });
    }
});
