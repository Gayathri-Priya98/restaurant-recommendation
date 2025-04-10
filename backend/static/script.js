// Leaflet.js Map Initialization (India default center)
var map = L.map('map').setView([20, 78], 5); 

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// User location fetch and display
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
        let userLat = position.coords.latitude;
        let userLng = position.coords.longitude;

        map.setView([userLat, userLng], 12); // Zoom to user location

        // Fetch nearby restaurants from Flask API
        fetch(`/restaurants?lat=${userLat}&lng=${userLng}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(restaurant => {
                    L.marker([restaurant.latitude, restaurant.longitude]).addTo(map)
                        .bindPopup(`<h3>${restaurant.name}</h3>
                                    <p>⭐ ${restaurant.stars} Stars</p>
                                    <p>${restaurant.address}</p>`);
                });
            })
            .catch(error => console.error("Error fetching restaurants:", error));
    });
} else {
    alert("Geolocation is not supported by this browser.");
}

// Search by city function
function searchByCity() {
    let city = document.getElementById('city').value;

    fetch(`/restaurants?city=${city}`)
        .then(response => response.json())
        .then(data => showRestaurantsOnMap(data))
        .catch(error => console.error("Error fetching restaurants:", error));
}

// Display restaurants on map
function showRestaurantsOnMap(data) {
    data.forEach(restaurant => {
        L.marker([restaurant.latitude, restaurant.longitude]).addTo(map)
            .bindPopup(`<h3>${restaurant.name}</h3>
                        <p>⭐ ${restaurant.stars} Stars</p>
                        <p>${restaurant.address}</p>`);
    });
}
