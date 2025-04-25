import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-defaulticon-compatibility';
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css';
import axios from 'axios';
import L from 'leaflet';
import './App.css';

// ✅ Custom green icon for nearby restaurants
const greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// ✅ Custom red icon for other restaurants
const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// 🔽 FitBounds component
const FitBounds = ({ locations }) => {
  const map = useMap();

  useEffect(() => {
    if (locations.length > 0) {
      const bounds = locations.map(loc => [loc.lat, loc.lng]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [locations, map]);

  return null;
};
const mapContainerStyle = { width: '100%', height: '400px', marginBottom: '1rem' };

function App() {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState({ lat: 14.91, lng: 78.00 });
  const [nearbyRestaurants, setNearbyRestaurants] = useState([]);
  const [otherRestaurants, setOtherRestaurants] = useState([]);

  // ✅ Auto-detect user location
  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLoc = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        console.log("📍 User Location:", userLoc); 
        setLocation(userLoc);
      },
      (error) => {
        console.error("Location access denied!", error);
        alert("Location permission required to get nearby restaurants.");
      }
    );
  }, []);
  

  // ✅ Handle Search
  const handleSearch = async () => {
    console.log("Sending request with:", query, location);
    if (!query.trim()) {
      alert("Please enter a search term!");
      return;
    }

    try {
      const response = await axios.get('http://localhost:5000/search', {
        params: {
          query,
          lat: location.lat,
          lng: location.lng
        }
      });

      setNearbyRestaurants(response.data.nearby || []);
      setOtherRestaurants(response.data.others || []);
    } catch (error) {
      console.error("Error fetching restaurants", error);
    }
  };

  const allRestaurants = [...nearbyRestaurants, ...otherRestaurants];

  return (
    <div className="container">
      <h1>🍔 Restaurant Finder</h1>

      {/* ✅ Leaflet Map */}
      <MapContainer center={location} zoom={13} style={mapContainerStyle}>
  <TileLayer
    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    attribution="&copy; OpenStreetMap contributors"
  />

  {/* User location */}
  <Marker position={location}>
    <Popup>
    📍current location<br />
      Lat: {location.lat.toFixed(4)}<br />
      Lng: {location.lng.toFixed(4)}
    </Popup>
  </Marker>

  {/* Markers */}
  {nearbyRestaurants.map((rest, index) => (
    <Marker
      key={`nearby-${index}`}
      position={{ lat: rest.latitude, lng: rest.longitude }}
      icon={greenIcon}
    >
      <Popup>
        <strong>{rest.name}</strong><br />
        ⭐ {rest.stars} <br />
        📍 {rest.distance} km
      </Popup>
    </Marker>
  ))}
  {otherRestaurants.map((rest, index) => (
    <Marker
      key={`other-${index}`}
      position={{ lat: rest.latitude, lng: rest.longitude }}
      icon={redIcon}
    >
      <Popup>
        <strong>{rest.name}</strong><br />
        ⭐ {rest.stars} <br />
        📍 {rest.distance} km
      </Popup>
    </Marker>
  ))}

  {/* ✅ Auto-fit all markers */}
  <FitBounds locations={[
    { lat: location.lat, lng: location.lng },
    ...nearbyRestaurants.map(r => ({ lat: r.latitude, lng: r.longitude })),
    ...otherRestaurants.map(r => ({ lat: r.latitude, lng: r.longitude })),
  ]} />
</MapContainer>

      <input
        type="text"
        placeholder="Search for biryani, dosa, pizza..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSearch}>Search</button>

      {allRestaurants.length > 0 ? (
        allRestaurants.map((rest, index) => (
          <div key={index} className="result-card">
            <h3>{rest.name}</h3>
            <p>⭐ Rating: {rest.stars}</p>
            <p>📍 Distance: {rest.distance} km</p>
          </div>
        ))
      ) : (
        <p>No results yet. Try searching something!</p>
      )}

      <footer>Built with ❤️ </footer>
    </div>
  );
}

export default App;
