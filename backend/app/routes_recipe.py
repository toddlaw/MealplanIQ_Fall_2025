from flask import Blueprint, jsonify, request
import csv, os
from pathlib import Path
import pymysql
from user_db.user_db import DatabaseManager

bp = Blueprint("recipes", __name__, url_prefix="/api")

CSV_DIR = (Path(__file__).resolve().parent / ".." / ".." / "custom_recipes"/"nutrients").resolve()
ING_DIR = (Path(__file__).resolve().parent / ".." / ".." / "custom_recipes"/"ingredients").resolve()
INST_DIR = (Path(__file__).resolve().parent / ".." / ".." / "custom_recipes"/"instructions").resolve()
print(f"[recipes] CSV_DIR = {CSV_DIR}")

def get_conn():
    dbm = DatabaseManager()
    dbm.db.ping(reconnect=True)
    return dbm.db

# MUST match your custom_recipes schema
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
    "vitiamin_D_IU", "vitamin_D2D3_g", "vitamin_D2_ergocalciferol_g",
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

def _safe_path(base: Path, p: Path) -> Path:
    p = p.resolve()
    if base not in p.parents and p != base:
        raise ValueError("Unsafe path")
    return p

def _ing_path(user_id: str, number: int) -> Path:
    return _safe_path(ING_DIR, (ING_DIR / f"{user_id}_{number}_ingredients.csv"))

def _inst_path(user_id: str, number: int) -> Path:
    return _safe_path(INST_DIR, (INST_DIR / f"{user_id}_{number}_instructions.csv"))

def _ensure_dirs():
    os.makedirs(ING_DIR, exist_ok=True)
    os.makedirs(INST_DIR, exist_ok=True)

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
    ing_file = _ing_path(user_id, number)
    inst_file = _inst_path(user_id, number)

    ingredients = []
    if ing_file.exists():
        with ing_file.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                lr = { (k or "").strip().lower(): v for k, v in row.items() }
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

    instructions = []
    if inst_file.exists():
        with inst_file.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                lr = { (k or "").strip().lower(): v for k, v in row.items() }
                text = _lk(lr, "instruction", None)
                if text is None or str(text).strip() == "":
                    text = _lk(lr, "step", "")
                instructions.append(str(text))

    return jsonify({"ingredients": ingredients, "instructions": instructions})



@bp.put("/recipes/<user_id>/<int:number>/files")
def put_recipe_files(user_id: str, number: int):
    """
    Body:
      {
        ingredients: [{
          name, amount, unit, note,
          energy_kcal?, carbohydrates?, protein_g?, fat_g?
        }],
        instructions: [string]
      }
    Overwrites the two CSVs for this recipe with the EXACT required headers.
    """
    data = request.get_json(silent=True) or {}
    ingredients = data.get("ingredients") or []
    instructions = data.get("instructions") or []

    _ensure_dirs()

    # --- write Ingredients CSV with exact headers ---
    ing_file = _ing_path(user_id, number)
    with ing_file.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ING_HEADERS)
        w.writeheader()
        for ing in ingredients:
            # UI core fields
            name   = (ing.get("name") or "").strip()
            qty    = ing.get("amount") if ing.get("amount") is not None else ""
            unit   = (ing.get("unit") or "").strip()
            state  = (ing.get("note") or "").strip()  # map UI note -> State

            # Optional preserved fields (write blanks if not provided)
            energy_kcal   = ing.get("energy_kcal", "")
            carbohydrates = ing.get("carbohydrates", "")
            protein_g     = ing.get("protein_g", "")
            fat_g         = ing.get("fat_g", "")

            w.writerow({
                "Ingredient Name":       name,
                "Quantity":              qty,
                "Unit":                  unit,
                "State":                 state,
                "Energy (kcal)":         energy_kcal,
                "Carbohydrates":         carbohydrates,
                "Protein (g)":           protein_g,
                "Total Lipid (Fat) (g)": fat_g,
            })

    # --- write Instructions CSV with exact headers ---
    inst_file = _inst_path(user_id, number)
    with inst_file.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=INST_HEADERS)
        w.writeheader()
        for idx, text in enumerate(instructions, start=1):
            w.writerow({
                "Step": idx,
                "Instruction": (text or "").strip(),
            })

    return jsonify({"ok": True})


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

def _sync_all_csvs(mode: str = "update"):
    """
    Scan CSV_DIR, read first row of each CSV, and upsert user-agnostically.
    Requires each CSV to include a 'user_id' field to know who owns the row.
    """
    csv_files = sorted([p for p in CSV_DIR.glob("*.csv") if p.is_file()])
    if not csv_files:
        return {"ok": True, "files": 0, "inserted_or_updated": 0, "skipped": 0}

    conn = get_conn()
    inserted_or_updated = 0
    skipped = 0
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        for path in csv_files:
            try:
                with open(path, encoding="utf-8") as f:
                    r = csv.DictReader(f)
                    raw = next(r, None)
                    if not raw:
                        continue
                    data = _normalize_headers(raw)

                    # We expect CSVs to carry their own user_id (since this sync is user-agnostic)
                    csv_user = (data.get("user_id") or "").strip()
                    if not csv_user:
                        # No user_id in file; we can't place it → skip
                        print(f"[recipes-sync] SKIP {path.name}: missing user_id")
                        skipped += 1
                        continue

                    res = _upsert_row(cur, data, mode=mode)
                    if res.get("ok"):
                        if res.get("skipped"):
                            skipped += 1
                        else:
                            inserted_or_updated += 1
                    else:
                        skipped += 1
                        print(f"[recipes-sync] SKIP {path.name}: {res}")
            except Exception as e:
                skipped += 1
                print(f"[recipes-sync] ERROR in {path.name}: {e!r}")

        conn.commit()

    return {"ok": True, "files": len(csv_files), "inserted_or_updated": inserted_or_updated, "skipped": skipped}

# Optional manual trigger (handy for testing)
@bp.post("/recipes/sync")
def manual_sync():
    mode = (request.json or {}).get("mode") or "update"
    out = _sync_all_csvs(mode=mode)
    return jsonify(out)

@bp.get("/recipes")
def list_recipes():
    """
    Auto-sync all CSVs (user-agnostic) on every page load,
    then return recipes for the requested user_id only.
    """
    # Auto-sync first (update existing or insert new)
    _ = _sync_all_csvs(mode="update")

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
