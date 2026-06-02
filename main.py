import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# A simple API endpoint that your JavaScript frontend will call
@app.get("/api/hello")
async def hello_backend():
    return {"message": "On-Inn! Hello from the Python backend running on Render!"}

# Serve everything inside the 'static' folder at the root URL '/'
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
