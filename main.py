import math
import random
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
    
    # 1. Query the Isochrone endpoint for a 35-minute outward boundary
    target_time_seconds = 2100 
    isochrone_url = "https://api.openrouteservice.org/v2/isochrones/foot-hiking"
    
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    
    isochrone_body = {
        "locations": [[start_lng, start_lat]],
        "range": [target_time_seconds],
        "range_type": "time"
    }
    
    try:
        # Fetch the physical footprint of reachable paths
        req = urllib.request.Request(isochrone_url, data=json.dumps(isochrone_body).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            iso_result = json.loads(response.read().decode('utf-8'))
            
        boundary_geometry = iso_result['features'][0]['geometry']['coordinates'][0]
        
        # 2. Rotational Sampling Math
        # Roll a random base angle in radians (0 to 2*pi)
        base_angle = random.uniform(0, 2 * math.pi)
        
        # Define 3 target angles spaced 120 degrees (2*pi / 3) apart
        target_angles = [
            base_angle,
            base_angle + (2 * math.pi / 3),
            base_angle + (4 * math.pi / 3)
        ]
        
        # Anchors to store our best coordinate matches
        waypoints = []
        
        # For each target angle, find the point in the polygon closest to that heading
        for target_ang in target_angles:
            best_point = None
            best_difference = float('inf')
            
            for pt in boundary_geometry:
                lng, lat = pt[0], pt[1]
                
                # Calculate angle from pub to this polygon point
                angle = math.atan2(lat - start_lat, lng - start_lng)
                if angle < 0:
                    angle += 2 * math.pi
                    
                # Find absolute difference between point angle and our target vector
                diff = abs(angle - (target_ang % (2 * math.pi)))
                diff = min(diff, 2 * math.pi - diff) # Handle wrap-around
                
                if diff < best_difference:
                    best_difference = diff
                    best_point = [lng, lat]
                    
            if best_point:
                waypoints.append(best_point)

        # 3. Request actual Directions connecting our 3 discovered anchors
        directions_url = "https://api.openrouteservice.org/v2/directions/foot-hiking/geojson"
        
        directions_body = {
            "coordinates": [
                [start_lng, start_lat], # Start at pub
                waypoints[0],           # Outbound Anchor 1
                waypoints[1],           # Outbound Anchor 2
                waypoints[2],           # Outbound Anchor 3
                [start_lng, start_lat]  # Back to pub
            ]
        }
        
        req_dir = urllib.request.Request(directions_url, data=json.dumps(directions_body).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req_dir) as response:
            dir_result = json.loads(response.read().decode('utf-8'))
            
        geometry = dir_result['features'][0]['geometry']['coordinates']
        trail_line = [[pt[1], pt[0]] for pt in geometry]
        
        return {
            "status": "success",
            "message": "Randomized, network-aware trail loop generated!",
            "trail": trail_line
        }
        
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'read'):
            try:
                error_details = e.read().decode('utf-8')
            except Exception:
                pass
        print(f"Routing Error: {error_details}")
        return {
            "status": "error",
            "message": f"Failed to calculate loop: {error_details}",
            "trail": []
        }



app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
