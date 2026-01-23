from flask import Blueprint, jsonify, request, send_file
from typing import Optional
import re
import csv, os
import io
from pathlib import Path
import pymysql
from user_db.user_db import DatabaseManager
from app.custom_recipe.nutrition_calc import calc_nutrition, extract_ingredients_for_calc
from .mealplan_service import read_blob_bytes_from_gcs, read_blob_text_from_gcs, _upload_csv_string_to_gcs
from io import BytesIO



bp = Blueprint("recipes", __name__, url_prefix="/api")

CUSTOM_BUCKET = "meal-plan-data"
CUSTOM_BASE_PREFIX = "meal_db"


def _gcs_ing_blob(user_id: str, number: int) -> str:
    return f"{CUSTOM_BASE_PREFIX}/ingredients/{user_id}_{number}_ingredients.csv"

def _gcs_inst_blob(user_id: str, number: int) -> str:
    return f"{CUSTOM_BASE_PREFIX}/instructions/{user_id}_{number}_instructions.csv"

def get_conn():
    dbm = DatabaseManager()
    dbm.db.ping(reconnect=True)
    return dbm.db

TABLE_COLUMNS = {
    "user_id", "number", "meal_type", "meal_slot", "title",
    "energy_kcal", "energy_kj", "fibre_g", "carbohydrates_g", "starch_g",
    "cholesterol_mg", "betasitosterol_mg", "campesterol_mg", "stigmasterol_mg",
    "phytosterols_mg", "sugars_total_g", "fructose_g", "galactose_g", "glucose_g",
    "lactose_g", "maltose_g", "sucrose_g", "water_g", "protein_g", "protein_adjusted_g",
    "alanine_g", "arginine_g", "aspartic_acid_g", "betaine_g", "cystine_g",
    "glutamic_acid_g", "glycine_g", "histidine_g", "hydroxyproline_g", "isoleucine_g",
    "leucine_g", "lysine_g", "methionine_g", "phenylanine_g", "proline_g",
    "serine_g", "theonine_g", "tryptophan_g", "tyrosine_g", "valine_g",
    "calcium_mg", "phosphorus_mg", "potassium_mg", "magnesium_mg", "sodium_mg",
    "iron_mg", "copper_mg", "zinc_mg", "manganese_mg", "selenium_ug", "fluoride_mg",
    "ash_g", "vitamin_A_iu", "vitamin_A_RAE_g", "vitamin_A1_retinol_g", "thiamin_mg",
    "riboflavin_mg", "niacin_mg", "vitamin_B5_pantothenic_acid_mg", "vitamin_B6_mg",
    "vitamin_B12_added_ug", "vitamin_B12_ug", "folate_DFE_ug", "folate_food_ug",
    "folate_total_ug", "folic_acid_g", "vitamin_C_total_ascorbic_acid_mg",
    "vitiamin_D_IU", "vitamin_D2D3_ug", "vitamin_D2_ergocalciferol_g",
    "vitamin_E_alphatocopherol_mg", "vitamin_E_added_mg", "tocopherol_beta_mg",
    "tocopherol_delta_mg", "tocopherol_gamma_mg", "tocotrienol_alpha_mg",
    "tocotrienol_beta_mg", "tocotrienol_delta_mg", "tocotrienol_gamma_mg",
    "vitamin_K_phylloquinone_ug", "vitamin_K2_menaquinone4_g", "choline_mg",
    "carotene_alpha_g", "carotene_beta_g", "lutein_zeaxanthin_g", "lycophene_g",
    "fats_total_g", "fats_lipid_g", "fatty_acids_total_monounsaturated_g",
    "fatty_acids_total_polyunsaturated_g", "fatty_acids_total_saturated_g",
    "region", "subregion", "country",
    "cooktime", "preptime", "ingredients", "approximate_total_cost",
    "individual_ingredient_costs", "ingredients_with_quantities",
    "cooking_instructions",
    "sports_build_muscle_score", "fight_heart_disease_score", "fight_diabetes_score",
    "fight_cancer_score", "lose_weight_score",
}


def _lk(lower_row: dict, key: str, default=""):
    """Lookup using a row whose keys are already lower-cased."""
    return lower_row.get((key or "").strip().lower(), default)

# These are the EXACT headers we will write for ingredients
ING_HEADERS = [
    "Ingredient Name",
    "Quantity",
    "Unit",
    "State",
    "Energy (kcal)",
    "Carbohydrates",
    "Protein (g)",
    "Total Lipid (Fat) (g)",
]

# These are the EXACT headers we will write for instructions
INST_HEADERS = ["Step", "Instruction"]


@bp.get("/recipes/<user_id>/<int:number>/files")
def get_recipe_files(user_id: str, number: int):
    ing_blob = _gcs_ing_blob(user_id, number)
    inst_blob = _gcs_inst_blob(user_id, number)

    ingredients = []
    try:
        ing_text = read_blob_text_from_gcs(CUSTOM_BUCKET, ing_blob)
        f = io.StringIO(ing_text)
        r = csv.DictReader(f)
        for row in r:
            lr = {(k or "").strip().lower(): v for k, v in row.items()}
            ingredients.append({
                "name":          _lk(lr, "ingredient name", ""),
                "amount":        _lk(lr, "quantity", ""),
                "unit":          _lk(lr, "unit", ""),
                "note":          _lk(lr, "state", ""),
                "energy_kcal":   _lk(lr, "energy (kcal)", ""),
                "carbohydrates": _lk(lr, "carbohydrates", ""),
                "protein_g":     _lk(lr, "protein (g)", ""),
                "fat_g":         _lk(lr, "total lipid (fat) (g)", ""),
            })
    except FileNotFoundError:
        pass

    instructions = []
    try:
        inst_text = read_blob_text_from_gcs(CUSTOM_BUCKET, inst_blob)
        f = io.StringIO(inst_text)
        r = csv.DictReader(f)
        for row in r:
            lr = {(k or "").strip().lower(): v for k, v in row.items()}
            text = _lk(lr, "instruction", None)
            if text is None or str(text).strip() == "":
                text = _lk(lr, "step", "")
            instructions.append(str(text))
    except FileNotFoundError:
        pass

    return jsonify({"ingredients": ingredients, "instructions": instructions})



@bp.put("/recipes/<user_id>/<int:number>/files")
def put_recipe_files(user_id: str, number: int):
    data = request.get_json(silent=True) or {}
    ingredients = data.get("ingredients") or []
    instructions = data.get("instructions") or []

    # --- build Ingredients CSV in memory ---
    ing_buffer = io.StringIO()
    w = csv.DictWriter(ing_buffer, fieldnames=ING_HEADERS)
    w.writeheader()

    for ing in ingredients:
        name   = (ing.get("name") or "").strip()
        qty    = ing.get("amount") if ing.get("amount") is not None else ""
        unit   = (ing.get("unit") or "").strip()
        state  = (ing.get("note") or "").strip()

        w.writerow({
            "Ingredient Name":       name,
            "Quantity":              qty,
            "Unit":                  unit,
            "State":                 state,
            "Energy (kcal)":         ing.get("energy_kcal", ""),
            "Carbohydrates":         ing.get("carbohydrates", ""),
            "Protein (g)":           ing.get("protein_g", ""),
            "Total Lipid (Fat) (g)": ing.get("fat_g", ""),
        })

    ingredients_csv = ing_buffer.getvalue()

    # --- build Instructions CSV in memory ---
    inst_buffer = io.StringIO()
    w = csv.DictWriter(inst_buffer, fieldnames=INST_HEADERS)
    w.writeheader()

    for idx, text in enumerate(instructions, start=1):
        w.writerow({
            "Step": idx,
            "Instruction": (text or "").strip(),
        })

    instructions_csv = inst_buffer.getvalue()

    # --- upload both CSVs to GCS ---
    ingredients_filename  = f"{user_id}_{number}_ingredients.csv"
    instructions_filename = f"{user_id}_{number}_instructions.csv"

    _upload_csv_string_to_gcs(
        "meal-plan-data",
        f"meal_db/ingredients/{ingredients_filename}",
        ingredients_csv,
    )
    _upload_csv_string_to_gcs(
        "meal-plan-data",
        f"meal_db/instructions/{instructions_filename}",
        instructions_csv,
    )

    # -------------------------
    # ✅ DB update (sync fields)
    # -------------------------
    # cooking_instructions: list -> newline string
    cooking_instructions = "\n".join(
        [str(x).strip() for x in instructions if str(x).strip()]
    ) or None

    # ingredients strings (DB format)
    # NOTE: _build_ingredients_strings expects raw items like {name, quantity/unit...}
    # your UI uses amount, so map to quantity for that helper
    raw_for_build = []
    for ing in ingredients:
        raw_for_build.append({
            "name": ing.get("name"),
            "quantity": ing.get("amount"),  # important
            "unit": ing.get("unit"),
        })

    ingredients_str, ingredients_with_qty_str = _build_ingredients_strings(raw_for_build)

    # If you want nutrition totals updated too, you can also re-run calc_nutrition here
    # (optional; commented out to keep PUT fast)
    # ingredients_for_calc = extract_ingredients_for_calc(raw_for_build)
    # nut = calc_nutrition(ingredients_for_calc)
    # totals = nut.get("totals") or {}
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE custom_recipes
            SET ingredients=%s,
                ingredients_with_quantities=%s,
                cooking_instructions=%s
            WHERE user_id=%s AND `number`=%s
        """, (ingredients_str, ingredients_with_qty_str, cooking_instructions, user_id, number))
        conn.commit()

    res = {"rows_affected": cur.rowcount}

    return jsonify({"ok": True, "db": res})




def _coerce(v):
    if v is None:
        return None
    v = str(v).strip()
    if v == "" or v.lower() == "null":
        return None
    try:
        if "." in v:
            return float(v)
        return int(v)
    except:
        return v

def _normalize_headers(row_dict):
    # lower-case, stripped keys
    return {(k or "").strip().lower(): (v if v is not None else "") for k, v in row_dict.items()}

def _next_number_for_user(cur, uid: str) -> int:
    cur.execute("SELECT COALESCE(MAX(`number`),0) AS mx FROM custom_recipes WHERE user_id=%s", (uid,))
    return int(cur.fetchone()["mx"] or 0) + 1

def _find_number_by_title(cur, uid: str, title: str):
    cur.execute("SELECT `number` FROM custom_recipes WHERE user_id=%s AND title=%s LIMIT 1", (uid, title))
    row = cur.fetchone()
    return int(row["number"]) if row else None

def _row_exists(cur, uid: str, num: int) -> bool:
    cur.execute("SELECT 1 FROM custom_recipes WHERE user_id=%s AND `number`=%s LIMIT 1", (uid, num))
    return bool(cur.fetchone())

def _upsert_row(cur, data: dict, mode: str = "update"):
    """
    data: dict of normalized, coerced values containing at least user_id and title (and optionally number)
    mode: 'update' (insert or update) or 'skip' (insert if new, do nothing if exists)
    """
    user_id = data.get("user_id")
    if not user_id:
        return {"ok": False, "skipped": True, "reason": "missing user_id in CSV"}

    # Decide the record key (user_id, number)
    number = data.get("number")
    try:
        number = int(number) if number not in (None, "") else None
    except (TypeError, ValueError):
        number = None

    title = (data.get("title") or "").strip() or None

    if number is None:
        # Try to match by (user_id, title) to UPDATE existing
        if title:
            found = _find_number_by_title(cur, user_id, title)
            if found is not None:
                number = found
        # If still none, assign the next per user
        if number is None:
            number = _next_number_for_user(cur, user_id)

    # Build the clean row constrained to known columns
    row = {col: _coerce(data.get(col)) for col in TABLE_COLUMNS}
    row["user_id"] = user_id
    row["number"] = number
    row["title"] = row.get("title") or f"Imported Recipe #{number}"
    row["meal_type"] = row.get("meal_type") or "Lunch"
    row["meal_slot"] = row.get("meal_slot") or "Main"

    # Columns to send (only those with non-None values)
    columns = [c for c in TABLE_COLUMNS if row.get(c) is not None]
    # Ensure PK columns are present
    for pk in ("user_id", "number"):
        if pk not in columns:
            columns.append(pk)

    placeholders = ", ".join(["%s"] * len(columns))
    collist = ", ".join(f"`{c}`" for c in columns)
    non_pk_cols = [c for c in columns if c not in ("user_id", "number")]

    # If exists and skip -> do nothing
    if _row_exists(cur, user_id, number) and mode == "skip":
        return {"ok": True, "skipped": True, "user_id": user_id, "number": number}

    # Upsert on (user_id, number)
    if mode == "update" and non_pk_cols:
        update_clause = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in non_pk_cols)
        sql = f"INSERT INTO custom_recipes ({collist}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"
    else:
        sql = f"INSERT INTO custom_recipes ({collist}) VALUES ({placeholders})"

    cur.execute(sql, tuple(row[c] for c in columns))
    return {"ok": True, "skipped": False, "user_id": user_id, "number": number}

@bp.get("/recipes")
def list_recipes():
    """
    Auto-sync all CSVs (user-agnostic) on every page load,
    then return recipes for the requested user_id only.
    """
    # Auto-sync first (update existing or insert new)
    # _ = _sync_all_csvs(mode="update")

    user_id = request.args.get("user_id")
    where = "WHERE user_id=%s" if user_id else ""
    params = (user_id,) if user_id else ()

    conn = get_conn()

    
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(f"""
            SELECT user_id, `number`, title, meal_type, meal_slot
            FROM custom_recipes
            {where}
            ORDER BY user_id, `number`
        """, params)
        rows = cur.fetchall()

    return jsonify([
        {
            "id": str(r["number"]),
            "title": r["title"],
            "meal_type": r["meal_type"],
            "meal_slot": r["meal_slot"],
            "user_id": r["user_id"],
            "ingredients": [],
            "instructions": [],
        }
        for r in rows
    ])

@bp.post("/recipes/<user_id>")
def create_recipe(user_id):
    data = request.json or {}
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO custom_recipes (user_id, `number`, meal_type, meal_slot, title)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, data["id"], data["meal_type"], data["meal_slot"], data["title"]))
    conn.commit()
    return jsonify({"ok": True}), 201



# Following functions are used for custom recipes to show up in the Replace Search


TITLE_GUESS_FIELDS = ["title", "name", "recipe", "recipe_title"]

def _read_first_row_csv(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        with path.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            row = next(r, None)
            return row if row else None
    except Exception:
        return None

def _title_from_sources(cur, uid: str, number: int) -> str:
    cur.execute(
        "SELECT title FROM custom_recipes WHERE user_id=%s AND `number`=%s LIMIT 1",
        (uid, number),
    )
    row = cur.fetchone()
    if row and row.get("title"):
        return str(row["title"]).strip()
    return f"Custom Recipe {number}"

@bp.get("/custom-recipes/<user_id>/search")
def search_custom_recipes(user_id: str):
    """
    GET /api/custom-recipes/<user_id>/search?q=term&exact=true|false
    Returns: [{ id, title, cuisine?, __source: 'custom' }]
    """
    # keep DB in sync with local CSVs before searching
    # _ = _sync_all_csvs(mode="update")

    q = (request.args.get("q") or "").strip()
    exact = (request.args.get("exact") or "false").lower() == "true"

    params = [user_id]
    where = ["user_id=%s"]

    if q:
        if exact:
            # match title exactly OR match number exactly if q is numeric
            where.append("(title = %s OR `number` = %s)")
            if q.isdigit():
                params.extend([q, int(q)])
            else:
                params.extend([q, -1])  # number won't match
        else:
            where.append("(title LIKE %s OR CAST(`number` AS CHAR) LIKE %s)")
            like = f"%{q}%"
            params.extend([like, like])

    sql = f"""
        SELECT `number`, title, region, subregion, country
        FROM custom_recipes
        WHERE {' AND '.join(where)}
        ORDER BY `number`
        LIMIT 100
    """

    conn = get_conn()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

    # shape for Angular suggestions
    out = []
    for r in rows:
        cuisine = r.get("region") or r.get("subregion") or r.get("country")
        out.append({
            "id": int(r["number"]),
            "title": r["title"] or f"Custom Recipe {r['number']}",
            "cuisine": cuisine,
            "__source": "custom",
        })
    return jsonify(out)


@bp.get("/custom-recipes/<user_id>/<int:number>")
def get_custom_recipe(user_id: str, number: int):
    """
    Returns a dialog-ready payload with title + calories + cuisine +
    prep/cook time + ingredients + instructions.
    """
    conn = get_conn()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(
            """
            SELECT title,
                   energy_kcal,
                   meal_type,
                   region,
                   subregion,
                   country,
                   cooktime,
                   preptime
            FROM custom_recipes
            WHERE user_id=%s AND `number`=%s
            LIMIT 1
            """,
            (user_id, number),
        )
        row = cur.fetchone()

        title = None
        energy_kcal = None
        meal_type = None
        region = None
        subregion = None
        country = None
        cooktime = None
        preptime = None

        if row:
            title = (row.get("title") or "").strip() or None
            energy_kcal = row.get("energy_kcal")
            meal_type = row.get("meal_type")
            region = row.get("region")
            subregion = row.get("subregion")
            country = row.get("country")
            cooktime = row.get("cooktime")
            preptime = row.get("preptime")

        if not title:
            title = _title_from_sources(cur, user_id, number)

    cuisine = region or subregion or country

    # -------- Ingredients (GCS CSV) --------
    ingredients = []
    ing_blob = _gcs_ing_blob(user_id, number)
    try:
        ing_text = read_blob_text_from_gcs(CUSTOM_BUCKET, ing_blob)
        f = io.StringIO(ing_text)
        r = csv.DictReader(f)
        for row in r:
            lr = {(k or "").strip().lower(): v for k, v in row.items()}
            ingredients.append({
                "name":          _lk(lr, "ingredient name", ""),
                "amount":        _lk(lr, "quantity", ""),
                "unit":          _lk(lr, "unit", ""),
                "note":          _lk(lr, "state", ""),
                "energy_kcal":   _lk(lr, "energy (kcal)", ""),
                "carbohydrates": _lk(lr, "carbohydrates", ""),
                "protein_g":     _lk(lr, "protein (g)", ""),
                "fat_g":         _lk(lr, "total lipid (fat) (g)", ""),
            })
    except FileNotFoundError:
        pass  # no ingredients csv yet

    # -------- Instructions (GCS CSV) --------
    instructions = []
    inst_blob = _gcs_inst_blob(user_id, number)
    try:
        inst_text = read_blob_text_from_gcs(CUSTOM_BUCKET, inst_blob)
        f = io.StringIO(inst_text)
        r = csv.DictReader(f)
        for row in r:
            lr = {(k or "").strip().lower(): v for k, v in row.items()}
            text = _lk(lr, "instruction", None)
            if text is None or str(text).strip() == "":
                # fallback: sometimes step column contains the text
                text = _lk(lr, "step", "")
            instructions.append(str(text))
    except FileNotFoundError:
        pass  # no instructions csv yet

    return jsonify({
        "id": number,
        "title": title,
        "source": "custom",
        "calories": energy_kcal,
        "region": cuisine,
        "cook_time": cooktime,
        "prep_time": preptime,
        "ingredients": ingredients,
        "instructions": instructions,
    })

@bp.get("/custom-recipes/<user_id>/<int:number>/ingredients.csv")
def stream_custom_ingredients(user_id: str, number: int):
    blob_path = _gcs_ing_blob(user_id, number)
    try:
        data = read_blob_bytes_from_gcs(CUSTOM_BUCKET, blob_path)
    except FileNotFoundError:
        return jsonify({"error": "ingredients CSV not found"}), 404

    return send_file(
        BytesIO(data),
        mimetype="text/csv; charset=utf-8",
        as_attachment=False,
        download_name=f"{user_id}_{number}_ingredients.csv",
    )


@bp.get("/custom-recipes/<user_id>/<int:number>/instructions.csv")
def stream_custom_instructions(user_id: str, number: int):
    blob_path = _gcs_inst_blob(user_id, number)
    try:
        data = read_blob_bytes_from_gcs(CUSTOM_BUCKET, blob_path)
    except FileNotFoundError:
        return jsonify({"error": "instructions CSV not found"}), 404

    return send_file(
        BytesIO(data),
        mimetype="text/csv; charset=utf-8",
        as_attachment=False,
        download_name=f"{user_id}_{number}_instructions.csv",
    )

def _quote_py(s: str) -> str:
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"

def _build_ingredients_strings(raw_ingredients):
    """
    raw_ingredients: [{name, quantity, unit, ...}] (quantity string 가능)
    return:
      ingredients_str: "['water','lentil']"
      ingredients_with_qty_str: "['water',1.0,'lentil',0.5]"
    """
    items = []
    for it in (raw_ingredients or []):
        name = str(it.get("name", "")).strip()
        qty = extract_ingredients_for_calc([it])[0]["quantity"]  # parse_quantity 
        items.append((name, qty))

    ingredients_str = "[" + ", ".join(_quote_py(n) for (n, _) in items) + "]"
    ingredients_with_qty_str = "[" + ", ".join(
        f"{_quote_py(n)}, {float(qty)}" for (n, qty) in items
    ) + "]"
    return ingredients_str, ingredients_with_qty_str


@bp.route("/custom-recipes/<user_id>/<int:number>/save", methods=["PUT", "OPTIONS"])
def save_custom_recipe(user_id: str, number: int):

    if request.method == "OPTIONS":
        return ("", 204)

    body = request.get_json(silent=True) or {}

    title     = (body.get("title") or "").strip()
    meal_type = (body.get("meal_type") or "Lunch").strip()
    meal_slot = (body.get("meal_slot") or "Main").strip()

    region    = (body.get("region") or "").strip() or None
    subregion = (body.get("subregion") or "").strip() or None
    country   = (body.get("country") or "").strip() or None

    cooktime  = body.get("cooktime")
    preptime  = body.get("preptime")

    raw_ingredients = body.get("ingredients") or []
    instructions = body.get("instructions") or []

    if not isinstance(raw_ingredients, list) or len(raw_ingredients) == 0:
        return jsonify({"ok": False, "error": "ingredients must be a non-empty list"}), 400

    if isinstance(instructions, list):
        cooking_instructions = "\n".join(
            [str(x).strip() for x in instructions if str(x).strip()]
        )
    else:
        cooking_instructions = str(instructions or "").strip()

    ingredients_str, ingredients_with_qty_str = _build_ingredients_strings(raw_ingredients)

    ingredients_for_calc = extract_ingredients_for_calc(raw_ingredients)
    try:
        nut = calc_nutrition(ingredients_for_calc)
        per_ingredient = nut.get("per_ingredient") or []
        totals = nut.get("totals") or {}
    except Exception as e:
        return jsonify({"ok": False, "error": f"nutrition_calc_failed: {e!r}"}), 500

    # ✅ DB upsert payload
    data = {
        "user_id": user_id,
        "number": number,
        "title": title or f"Custom Recipe {number}",
        "meal_type": meal_type,
        "meal_slot": meal_slot,
        "region": region,
        "subregion": subregion,
        "country": country,
        "cooktime": cooktime,
        "preptime": preptime,
        "ingredients": ingredients_str,
        "ingredients_with_quantities": ingredients_with_qty_str,
        "cooking_instructions": cooking_instructions or None,
    }

    # totals -> TABLE_COLUMNS
    for k, v in (totals or {}).items():
        if k in TABLE_COLUMNS:
            data[k] = v

    conn = get_conn()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        res = _upsert_row(cur, data, mode="update")
        conn.commit()

    return jsonify({"ok": True, "result": res, "totals": totals, "per_ingredient": per_ingredient})
