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
    
    # Let's create a destination point roughly 1km North of the pub
    start_lat = coords.lat
    start_lng = coords.lng
    end_lat = coords.lat + 0.010  
    end_lng = coords.lng
    
    # OpenRouteService expects coordinates in [Longitude, Latitude] order
    url = "https://api.openrouteservice.org/v2/directions/foot-hiking/geojson"
    
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    
    # We send the start and end points as a pair of coordinates
    body = {
        "coordinates": [
            [start_lng, start_lat], 
            [end_lng, end_lat]
        ],
        "options": {
            "avoid_features": ["highways"]
        }
    }
    
    try:
        # Package and send the request over the web to ORS
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        # ORS sends back a massive "GeoJSON" object. 
        # We dig out the exact list of coordinates that make up the path.
        # It comes back as [Lng, Lat], so we flip them to [Lat, Lng] for Leaflet.
        geometry = result['features'][0]['geometry']['coordinates']
        trail_line = [[pt[1], pt[0]] for pt in geometry]
        
        return {
            "status": "success",
            "message": "Hiking route fetched successfully!",
            "trail": trail_line
        }
        
    except Exception as e:
        print(f"Routing Error: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch route: {str(e)}",
            "trail": []
        }

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
