import os
import json
import random
import urllib.request
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijg3NTRiYWRiY2IzNjRlYzI5NjI1OTZjYTYzZDRmNTlhIiwiaCI6Im11cm11cjY0In0="

class TrailRequest(BaseModel):
    lat: float
    lng: float
    distance_category: str = "medium"

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.post("/api/generate-trail")
async def generate_trail(req: TrailRequest):
    start_lat = req.lat
    start_lng = req.lng
    
    # Map distance dropdown selections to base target lengths and waypoint counts
    # Base lengths are offset to compensate for ORS route expansion
    distance_presets = {
        "short": {"length": 3000, "points": 6},   # Output: ~3km - 5km
        "medium": {"length": 4500, "points": 8},  # Output: ~5km - 8km
        "long": {"length": 7000, "points": 10}    # Output: ~8km - 12km
    }
    
    preset = distance_presets.get(req.distance_category, distance_presets["medium"])
    
    url = "https://api.openrouteservice.org/v2/directions/foot-hiking/geojson"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    
    random_seed = random.randint(1, 1000)
    
    body = {
        "coordinates": [[start_lng, start_lat]],
        "options": {
            "round_trip": {
                "length": preset["length"],
                "points": preset["points"],
                "seed": random_seed
            }
        }
    }
    
    try:
        url_req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        
        with urllib.request.urlopen(url_req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        feature = result['features'][0]
        geometry = feature['geometry']['coordinates']
        
        trail_line = [[pt[1], pt[0]] for pt in geometry]
        
        summary = feature['properties']['summary']
        dist_km = round(summary['distance'] / 1000, 2)
        
        return {
            "status": "success",
            "message": f"On-On! Trail generated: {dist_km} km",
            "trail": trail_line,
            "distance_km": dist_km
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
            "message": f"Failed to generate trail: {error_details}",
            "trail": []
        }

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
