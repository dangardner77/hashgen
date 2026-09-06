// Initialize map centered near Hayling/Emsworth
const map = L.map('map').setView([50.8473, -0.9824], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let startMarker = null;
let selectedCoords = null;

// Listen for user clicks on the map to set the Pub / "On-Inn"
map.on('click', function(e) {
    const lat = parseFloat(e.latlng.lat.toFixed(6));
    const lng = parseFloat(e.latlng.lng.toFixed(6));
    selectedCoords = { lat: lat, lng: lng };

    document.getElementById('coords').innerText = `Lat: ${lat}, Lng: ${lng}`;
    document.getElementById('sendBtn').disabled = false;

    if (startMarker) {
        startMarker.setLatLng(e.latlng);
    } else {
        startMarker = L.marker(e.latlng).addTo(map).bindPopup("<b>On-Inn!</b>").openPopup();
    }
});

// Send request to build the loop
document.getElementById('sendBtn').addEventListener('click', async () => {
    if (!selectedCoords) return;
    
    const responseStatus = document.getElementById('backendResponse');
    responseStatus.style.color = 'inherit';
    responseStatus.innerText = "Laying hash trail...";
    
    try {
        const response = await fetch('/api/generate-trail', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(selectedCoords)
        });
        
        const data = await response.json();
        responseStatus.innerText = data.message;
        
        // Remove previous route line if it exists
        if (window.currentTrailLine) {
            map.removeLayer(window.currentTrailLine);
        }
        
        if (data.trail && data.trail.length > 0) {
            window.currentTrailLine = L.polyline(data.trail, {
                color: '#d32f2f',   // Crimson red trail color
                weight: 5,
                opacity: 0.85,
                dashArray: '8, 6'   // Dashed trail line style
            }).addTo(map);
            
            // Adjust camera view comfortably around the generated route
            map.fitBounds(window.currentTrailLine.getBounds(), { padding: [40, 40] });
        }
        
    } catch (err) {
        responseStatus.style.color = 'red';
        responseStatus.innerText = "Failed to communicate with backend.";
        console.error(err);
    }
});
