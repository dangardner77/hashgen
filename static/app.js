// Initialize the map centered near Hayling/Emsworth
const map = L.map('map').setView([50.8473, -0.9824], 13);

// Load standard OpenStreetMap map tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let startMarker = null;
let selectedCoords = null;

// Listen for user clicks on the map to set the Pub / "On-Inn" location
map.on('click', function(e) {
    const lat = parseFloat(e.latlng.lat.toFixed(6));
    const lng = parseFloat(e.latlng.lng.toFixed(6));
    selectedCoords = { lat: lat, lng: lng };

    // Update coordinates in the UI panel
    const coordsDisplay = document.getElementById('coords');
    if (coordsDisplay) {
        coordsDisplay.innerText = `Lat: ${lat}, Lng: ${lng}`;
    }
    
    document.getElementById('sendBtn').disabled = false;

    if (startMarker) {
        startMarker.setLatLng(e.latlng);
    } else {
        startMarker = L.marker(e.latlng).addTo(map).bindPopup("<b>On-Inn!</b>").openPopup();
    }
});

// Button action to handle sending data and rendering the translucent boundary polygon
document.getElementById('sendBtn').addEventListener('click', async () => {
    if (!selectedCoords) return;
    
    const responseStatus = document.getElementById('backendResponse');
    responseStatus.style.color = 'inherit'; // Reset any error coloring
    responseStatus.innerText = "Mapping boundary zone...";
    
    // Query the DOM explicitly right now when the click happens
    const liveTimeInput = document.getElementById('timeInput');
    const targetMinutes = liveTimeInput ? parseInt(liveTimeInput.value, 10) : 35;
    
    // Package coordinates alongside the selected runtime limit
    const payload = {
        lat: selectedCoords.lat,
        lng: selectedCoords.lng,
        minutes: isNaN(targetMinutes) ? 35 : targetMinutes
    };
    
    try {
        const response = await fetch('/api/generate-trail', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        responseStatus.innerText = data.message;
        
        // Wipe away the previous boundary zone layer if it exists
        if (window.currentBoundaryZone) {
            map.removeLayer(window.currentBoundaryZone);
        }
        
        if (data.trail && data.trail.length > 0) {
            // Render as a semi-transparent shaded area (tactical overlay map)
            window.currentBoundaryZone = L.polygon(data.trail, {
                color: '#0055ff',      // Clean, bright boundary line
                fillColor: '#00aaff',  // Soft translucent blue core
                fillOpacity: 0.25,     // Kept low so maps, roads, and trails show cleanly underneath
                weight: 3
            }).addTo(map);
            
            // Adjust the map viewport cleanly around the outer limits of the shape
            map.fitBounds(window.currentBoundaryZone.getBounds());
        }
        
    } catch (err) {
        responseStatus.style.color = 'red';
        responseStatus.innerText = "Failed to communicate with backend.";
        console.error(err);
    }
});
