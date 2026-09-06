@app.post("/api/generate-trail")
async def generate_trail(coords: Coordinates):
    start_lat = coords.lat
    start_lng = coords.lng
    
    url = "https://api.openrouteservice.org/v2/directions/foot-hiking/geojson"
    
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    
    random_seed = random.randint(1, 1000)
    
    # Lowering length to 4500m compensates for ORS distance overshoots
    # Increasing points to 8 forces higher path frequency and maximum wiggles
    body = {
        "coordinates": [[start_lng, start_lat]],
        "options": {
            "round_trip": {
                "length": 4500,        # Target ~4.5km base to hit actual 5km-7.5km real-world output
                "points": 8,           # Higher waypoint density forces more bends, twists, and detours
                "seed": random_seed
            }
        }
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
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
