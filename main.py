import math
import os
import json
import urllib.request
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# Paste your OpenRouteService API key here
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijg3NTRiYWRiY2IzNjRlYzI5NjI1OTZjYTYzZDRmNTlhIiwiaCI6Im11cm11cjY0In0="

class Coordinates(BaseModel):
    lat: float
    lng: float

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.post("/api/generate-trail")
async def generate_trail(coords: Coordinates):
    start_lat = coords.lat
    start_lng = coords.lng
    
    # 1. Define rough offsets in degrees to build a ~4km-5km jagged loop
    # In the UK, 0.010 degrees latitude is roughly 1.1km North/South
    # 0.016 degrees longitude is roughly 1.1km East/West
    lat_offset = 0.010
    lng_offset = 0.016

    # 2. Calculate 3 distinct waypoints around the start point (a diamond pattern)
    # Waypoint 1: North-East
    wp1_lat = start_lat + lat_offset
    wp1_lng = start_lng + lng_offset
    
    # Waypoint 2: North-West (creates a sharp turn from WP1)
    wp2_lat = start_lat + (lat_offset * 1.3) # Slightly pushed north to skew the loop
    wp2_lng = start_lng - lng_offset
    
    # Waypoint 3: West-South-West
    wp3_lat = start_lat - (lat_offset * 0.2)
    wp3_lng = start_lng - (lng_offset * 0.8)

    url = "https://api.openrouteservice.org/v2/directions/foot-hiking/geojson"
    
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    
    # 3. Feed the sequence of coordinates to ORS to force a circular path
    body = {
        "coordinates": [
            [start_lng, start_lat], # Start at pub
            [wp1_lng, wp1_lat],     # Sharp turn 1
            [wp2_lng, wp2_lat],     # Sharp turn 2
            [wp3_lng, wp3_lat],     # Sharp turn 3
            [start_lng, start_lat]  # Back to pub
        ]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        geometry = result['features'][0]['geometry']['coordinates']
        trail_line = [[pt[1], pt[0]] for pt in geometry]
        
        return {
            "status": "success",
            "message": "Circular trail loop generated!",
            "trail": trail_line
        }
        
    except Exception as e:
        print(f"Routing Error: {e}")
        return {
            "status": "error",
            "message": f"Failed to calculate loop: {str(e)}",
            "trail": []
        }


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
