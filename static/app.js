const map = L.map('map').setView([50.8473, -0.9824], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let startMarker = null;
let selectedCoords = null;

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

document.getElementById('sendBtn').addEventListener('click', async () => {
    if (!selectedCoords) return;
    
    const responseStatus = document.getElementById('backendResponse');
    responseStatus.style.color = 'inherit';
    responseStatus.innerText = "Laying hash trail...";
    
    // Read selected distance category
    const distanceCategory = document.getElementById('distanceSelect').value;
    
    const payload = {
        lat: selectedCoords.lat,
        lng: selectedCoords.lng,
        distance_category: distanceCategory
    };
    
    try {
        const response = await fetch('/api/generate-trail', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        responseStatus.innerText = data.message;
        
        if (window.currentTrailLine) {
            map.removeLayer(window.currentTrailLine);
        }
        
        if (data.trail && data.trail.length > 0) {
            window.currentTrailLine = L.polyline(data.trail, {
                color: '#d32f2f',
                weight: 5,
                opacity: 0.85,
                dashArray: '8, 6'
            }).addTo(map);
            
            map.fitBounds(window.currentTrailLine.getBounds(), { padding: [40, 40] });
        }
        
    } catch (err) {
        responseStatus.style.color = 'red';
        responseStatus.innerText = "Failed to communicate with backend.";
        console.error(err);
    }
});
