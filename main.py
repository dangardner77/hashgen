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
    
    # Target: A 35-minute outward walk (2100 seconds)
    # This will form the boundary line for our network-aware loop
    target_time_seconds = 2100 

    url = "https://api.openrouteservice.org/v2/isochrones/foot-hiking"
    
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    
    body = {
        "locations": [[start_lng, start_lat]],
        "range": [target_time_seconds],
        "range_type": "time"
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        # Extract the outer boundary polygon coordinates from the GeoJSON response
        # The structure is: features -> geometry -> coordinates -> first ring
        boundary_geometry = result['features'][0]['geometry']['coordinates'][0]
        
        # Convert from [lng, lat] to Leaflet-friendly [lat, lng]
        boundary_line = [[pt[1], pt[0]] for pt in boundary_geometry]
        
        return {
            "status": "success",
            "message": "Isochrone network boundary discovered!",
            "trail": boundary_line  # Sending the raw boundary polygon to the frontend map
        }
        
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'read'):
            try:
                error_details = e.read().decode('utf-8')
            except Exception:
                pass
        print(f"Isochrone Error: {error_details}")
        return {
            "status": "error",
            "message": f"Failed to calculate network boundary: {error_details}",
            "trail": []
        }



app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
