from flask import Blueprint, jsonify, request
import pymysql
from user_db.user_db import DatabaseManager  

bp = Blueprint("recipes", __name__, url_prefix="/api")

def get_conn():
    dbm = DatabaseManager()      
    dbm.db.ping(reconnect=True)  
    return dbm.db

# Queries for custom_recipes table

@bp.get("/recipes")
def list_recipes():
    """
    Returns all recipes. Optionally filter by user_id with ?user_id=abc
    Maps DB columns -> { id, title, meal_type, meal_slot, user_id }
    """
    user_id = request.args.get("user_id")

    sql = """
        SELECT user_id, `number`, title, meal_type, meal_slot
        FROM custom_recipes
        {where}
        ORDER BY user_id, `number`
    """.format(where="WHERE user_id = %s" if user_id else "")

    params = (user_id,) if user_id else ()

    conn = get_conn()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    # normalize to what the UI expects
    out = [
        {
            "id": str(r["number"]),          # use your `number` as the recipe id
            "title": r["title"],
            "meal_type": r["meal_type"],
            "meal_slot": r["meal_slot"],
            "user_id": r["user_id"],
            # placeholder arrays so UI can work without null checks:
            "ingredients": [],
            "instructions": [],
        }
        for r in rows
    ]
    return jsonify(out)

@bp.post("/api/recipes/<user_id>")
def create_recipe(user_id):
    data = request.json
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO custom_recipes (user_id, `number`, meal_type, meal_slot, title)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, data["id"], data["meal_type"], data["meal_slot"], data["title"]))
    conn.commit()
    return jsonify({"ok": True}), 201
