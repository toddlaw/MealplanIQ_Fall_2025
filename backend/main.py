from app import app

@app.get("/_debug/routes")
def _debug_routes():
    return {"routes": [str(r) for r in app.url_map.iter_rules()]}
