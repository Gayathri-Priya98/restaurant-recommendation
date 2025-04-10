import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png'
});

function Map() {
  const [location, setLocation] = useState({ lat: null, lng: null });
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition((position) => {
      setLocation({
        lat: position.coords.latitude,
        lng: position.coords.longitude
      });
    }, (err) => {
      console.error("Location Error:", err);
    });
  }, []);

  const handleSearch = async () => {
    if (!location.lat || !location.lng || !query) return;

    try {
      const res = await axios.get(`http://localhost:5000/search`, {
        params: {
          lat: location.lat,
          lng: location.lng,
          query: query
        }
      });
      setResults(res.data);
    } catch (err) {
      console.error("Search Error:", err);
    }
  };

  return (
    <div className="map-container">
      <div className="map-section">
        {/* Search bar as overlay on map */}
        <div className="search-bar-overlay">
          <input
            type="text"
            placeholder="Search food or restaurant..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button onClick={handleSearch}>Search</button>
        </div>

        {/* MAP */}
        {location.lat && location.lng && (
          <MapContainer
            center={[location.lat, location.lng]}
            zoom={14}
            scrollWheelZoom={true}
            className="leaflet-container"
          >
            <TileLayer
              url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
              attribution='&copy; OpenStreetMap contributors'
            />
            <Marker position={[location.lat, location.lng]}>
              <Popup>Current Location</Popup>
            </Marker>
            {results.map((res, idx) => (
              <Marker key={idx} position={[res.latitude, res.longitude]}>
                <Popup>
                  <strong>{res.name}</strong><br />
                  Rating: ⭐ {res.stars}<br />
                  Distance: 📍 {res.distance} km
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        )}
      </div>
    </div>
  );
}

export default Map;
