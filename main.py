import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# Define what data we expect from the frontend map
class Coordinates(BaseModel):
    lat: float
    lng: float

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/api/hello")
async def hello_backend():
    return {"message": "On-Inn! Hello from the Python backend running on Render!"}

# The new endpoint to receive map clicks
@app.post("/api/generate-trail")
async def generate_trail(coords: Coordinates):
    # For now, we will just log it and echo it back to the map
    print(f"Received On-Inn coordinates: Lat {coords.lat}, Lng {coords.lng}")
    
    return {
        "status": "success",
        "message": f"Backend received coordinates ({coords.lat}, {coords.lng}). Next step: plotting the loop!"
    }

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
