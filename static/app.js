// Initialize the map centered near Hayling/Emsworth
const map = L.map('map').setView([50.8473, -0.9824], 13);

// Load standard OpenStreetMap map tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let startMarker = null;
let selectedCoords = null;

// Listen for user clicks on the map
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

// Button action to handle and draw the trail lines
document.getElementById('sendBtn').addEventListener('click', async () => {
    if (!selectedCoords) return;
    
    const responseStatus = document.getElementById('backendResponse');
    responseStatus.innerText = "Calculating trail...";
    
    try {
        const response = await fetch('/api/generate-trail', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(selectedCoords)
        });
        
        const data = await response.json();
        responseStatus.innerText = data.message;
        
        if (window.currentTrailLine) {
            map.removeLayer(window.currentTrailLine);
        }
        
        if (data.trail) {
            window.currentTrailLine = L.polyline(data.trail, {
                color: 'blue',
                weight: 4,
                opacity: 0.7
            }).addTo(map);
            
            map.fitBounds(window.currentTrailLine.getBounds());
        }
        
    } catch (err) {
        responseStatus.style.color = 'red';
        responseStatus.innerText = "Failed to communicate with backend.";
        console.error(err);
    }
});
