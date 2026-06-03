import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

class Coordinates(BaseModel):
    lat: float
    lng: float

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.post("/api/generate-trail")
async def generate_trail(coords: Coordinates):
    # A tiny shift value (roughly 800 meters to 1km out)
    offset = 0.008 
    
    # Generate 3 waypoints forming a rough triangle circuit starting and ending at the pub
    waypoint_1 = [coords.lat, coords.lng]                      # The Pub (Start)
    waypoint_2 = [coords.lat + offset, coords.lng + offset]    # North-East
    waypoint_3 = [coords.lat - offset, coords.lng + offset]    # South-East
    waypoint_4 = [coords.lat, coords.lng]                      # Back to the Pub (End)
    
    # Put them in a list (an array of coordinates)
    trail_line = [waypoint_1, waypoint_2, waypoint_3, waypoint_4]
    
    return {
        "status": "success",
        "message": "Rough circuit calculated by Python!",
        "trail": trail_line
    }

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
