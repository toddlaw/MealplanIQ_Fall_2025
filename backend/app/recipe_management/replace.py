"""
Provides logic for replacing a recipe in a meal plan and updating nutritional values.

@author: BCIT May 2025
"""

import ast
import time
import csv
from pathlib import Path

import pandas as pd
import pymysql
from flask import jsonify

from app.generate_meal_plan import gen_shopping_list, insert_status_nutrient_info
from app.find_matched_recipe_and_update import update_nutrition_values
from user_db.user_db import DatabaseManager


# ---------- helpers for DB + custom CSVs ----------

def _get_conn():
    dbm = DatabaseManager()
    dbm.db.ping(reconnect=True)
    return dbm.db


# mirrors the directories in routes_recipe.py
BASE_DIR = Path(__file__).resolve().parent / ".." / ".."
ING_DIR = (BASE_DIR / "custom_recipes" / "ingredients").resolve()
INST_DIR = (BASE_DIR / "custom_recipes" / "instructions").resolve()


def _safe_path(base: Path, p: Path) -> Path:
    p = p.resolve()
    if base not in p.parents and p != base:
        raise ValueError("Unsafe path")
    return p


def _ing_path(user_id: str, number: int) -> Path:
    return _safe_path(ING_DIR, ING_DIR / f"{user_id}_{number}_ingredients.csv")


def _inst_path(user_id: str, number: int) -> Path:
    return _safe_path(INST_DIR, INST_DIR / f"{user_id}_{number}_instructions.csv")


def _lk(lower_row: dict, key: str, default=""):
    return lower_row.get((key or "").strip().lower(), default)


# The headers we wrote when saving ingredient CSVs
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


def _load_custom_recipe(user_id: str | None, number: int):
    """
    Build a recipe dict for a custom recipe so it looks like a row
    from meal_db/meal_database.csv + parsed ingredient/instruction lists.

    If user_id is None, we try to infer it from the custom_recipes table.
    """
    conn = _get_conn()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        if user_id:
            print(f"[_load_custom_recipe] Querying by explicit user_id={user_id}, number={number}")
            cur.execute(
                """
                SELECT *
                FROM custom_recipes
                WHERE user_id=%s AND `number`=%s
                LIMIT 1
                """,
                (user_id, number),
            )
        else:
            # Fallback: no user_id passed → infer from table
            print(f"[_load_custom_recipe] No user_id provided, inferring for number={number}")
            cur.execute(
                """
                SELECT *
                FROM custom_recipes
                WHERE `number`=%s
                LIMIT 1
                """,
                (number,),
            )

        row = cur.fetchone()

    if not row:
        print(f"[_load_custom_recipe][ERROR] No custom_recipes row found for user_id={user_id}, number={number}")
        return None

    # Ensure we always use the user_id from the row for CSV paths
    db_user_id = row.get("user_id")
    print(f"[_load_custom_recipe] Loaded row for user_id={db_user_id}, number={number}")

    recipe = dict(row)

    # Normalize key fields
    if recipe.get("energy_kcal") is not None:
        recipe["energy_kcal"] = float(recipe["energy_kcal"])

    # -------- Ingredients from CSV --------
    ingredients_with_quantities = []
    ing_file = _ing_path(db_user_id, number)
    if ing_file.exists():
        ingredients_with_quantities.append(ING_HEADERS[:])
        with ing_file.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                lr = {(k or "").strip().lower(): v for k, v in row.items()}
                ingredients_with_quantities.append([
                    _lk(lr, "ingredient name", ""),
                    _lk(lr, "quantity", ""),
                    _lk(lr, "unit", ""),
                    _lk(lr, "state", ""),
                    _lk(lr, "energy (kcal)", ""),
                    _lk(lr, "carbohydrates", ""),
                    _lk(lr, "protein (g)", ""),
                    _lk(lr, "total lipid (fat) (g)", ""),
                ])
    else:
        print(f"[_load_custom_recipe] WARNING: ingredients CSV not found at {ing_file}")

    recipe["ingredients_with_quantities"] = ingredients_with_quantities

    # -------- Instructions from CSV --------
    instructions = []
    inst_file = _inst_path(db_user_id, number)
    if inst_file.exists():
        with inst_file.open(newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                lr = {(k or "").strip().lower(): v for k, v in row.items()}
                text = _lk(lr, "instruction", None)
                if text is None or str(text).strip() == "":
                    text = _lk(lr, "step", "")
                instructions.append(str(text))
    else:
        print(f"[_load_custom_recipe] WARNING: instructions CSV not found at {inst_file}")

    recipe["instructions"] = instructions

    return recipe

# ---------- main entry point used by routes.py ----------

def replace_recipe_logic(data):
    """
    Replace a recipe in a specific position of a meal plan and update nutritional totals.
    """
    print("\n[replace-logic] ===== ENTER =====")
    print("[replace-logic] Incoming data type:", type(data))
    if isinstance(data, dict):
        print("[replace-logic] Incoming data keys:", list(data.keys()))
    else:
        print("[replace-logic] Incoming data value:", data)

    meal_plan = data.get("meal_plan")
    recipe_id_raw = data.get("recipe_id")
    day_index = data.get("day_index")
    recipe_index = data.get("recipe_index")

    print("[replace-logic] day_index:", day_index, "recipe_index:", recipe_index)
    print("[replace-logic] recipe_id_raw:", recipe_id_raw, "type:", type(recipe_id_raw))

    # ---------------- parse recipe_id / source ----------------
    source = "base"  # default behaviour: old recipes continue to work
    new_id = None
    explicit_user_id = data.get("user_id")

    print("[replace-logic] explicit_user_id from payload:", explicit_user_id)

    if isinstance(recipe_id_raw, dict):
        new_id = recipe_id_raw.get("id")
        source = recipe_id_raw.get("__source") or recipe_id_raw.get("source") or "base"
        if not explicit_user_id:
            explicit_user_id = recipe_id_raw.get("user_id")
        print("[replace-logic] recipe_id is dict -> new_id:", new_id, "source:", source, "explicit_user_id(now):", explicit_user_id)
    else:
        new_id = recipe_id_raw
        print("[replace-logic] recipe_id is NOT dict -> new_id:", new_id, "source(default):", source)

    if new_id is None:
        print("[replace-logic][ERROR] new_id is None -> returning 400 (Missing recipe id)")
        return jsonify({"error": "Missing recipe id", "debug": {"recipe_id_raw": str(recipe_id_raw)}}), 400

    try:
        new_id_int = int(new_id)
        print("[replace-logic] Parsed new_id_int:", new_id_int)
    except (TypeError, ValueError):
        print("[replace-logic][ERROR] Failed to cast new_id to int:", new_id)
        return jsonify({"error": f"Invalid recipe id: {new_id!r}"}), 400

    # try to infer user_id for custom recipes if not passed explicitly
    inferred_uid = explicit_user_id
    if not inferred_uid and isinstance(meal_plan, dict):
        inferred_uid = meal_plan.get("user_id")
    print("[replace-logic] inferred_uid:", inferred_uid)

    # ---------------- load base recipe dataframe (unchanged) -------------
    print("[replace-logic] Loading ./meal_db/meal_database.csv ...")
    recipe_df = pd.read_csv("./meal_db/meal_database.csv")
    print("[replace-logic] recipe_df loaded, shape:", recipe_df.shape)
    snack_recipes_df = recipe_df[recipe_df["meal_slot"] == "['snack']"]
    print("[replace-logic] snack_recipes_df shape:", snack_recipes_df.shape)

    # ---------------- remove old recipe from meal plan --------------------
    if not meal_plan or "days" not in meal_plan:
        print("[replace-logic][ERROR] meal_plan is missing or malformed:", meal_plan)
        return jsonify({"error": "Invalid meal_plan structure"}), 400

    try:
        old_recipe = meal_plan["days"][day_index]["recipes"].pop(recipe_index)
        print("[replace-logic] Popped old_recipe with id:", old_recipe.get("id"))

        # ---------------- ensure OLD recipe is in recipe_df -----------------
        try:
            old_id = int(old_recipe.get("id") or old_recipe.get("number"))
        except (TypeError, ValueError):
            old_id = None

        print(f"[replace-logic] old_recipe id: {old_id}")

        old_exists = False
        if old_id is not None:
            if "number" in recipe_df.columns:
                old_exists = not recipe_df.loc[recipe_df["number"] == old_id].empty
            elif "id" in recipe_df.columns:
                old_exists = not recipe_df.loc[recipe_df["id"] == old_id].empty

        if old_id is not None and not old_exists:
            print(
                f"[replace-logic] Injecting OLD recipe {old_id} into recipe_df for subtraction"
            )
            row_old = {}

            for col in recipe_df.columns:
                # Use value from old_recipe if present and not None
                if col in old_recipe and old_recipe[col] is not None:
                    row_old[col] = old_recipe[col]

                # Ensure primary key column is set
                elif col in ("number", "id"):
                    row_old[col] = old_id

                else:
                    # Default based on dtype: numeric -> 0, else None
                    col_series = recipe_df[col]
                    if pd.api.types.is_numeric_dtype(col_series.dtype):
                        row_old[col] = 0
                    else:
                        row_old[col] = None

            # Make sure energy_kcal is numeric if we have it
            if (
                "energy_kcal" in recipe_df.columns
                and old_recipe.get("energy_kcal") is not None
            ):
                row_old["energy_kcal"] = float(old_recipe["energy_kcal"])

            recipe_df = pd.concat(
                [recipe_df, pd.DataFrame([row_old])],
                ignore_index=True,
            )

            # Rebuild snack_recipes_df in case this old recipe is a snack
            if "meal_slot" in recipe_df.columns:
                snack_recipes_df = recipe_df[recipe_df["meal_slot"] == "['snack']"]

            print(
                "[replace-logic] recipe_df after OLD inject:",
                recipe_df.shape,
                "snack_recipes_df:",
                snack_recipes_df.shape,
            )

    except Exception as e:
        print("[replace-logic][ERROR] Failed to pop old_recipe:", repr(e))
        return jsonify({"error": "Could not locate recipe to replace", "details": str(e)}), 400

    # ---------------- build new_recipe for base vs custom -----------------
    if source == "custom":
        print("[replace-logic] Using CUSTOM recipe branch")
        print("[replace-logic] Loading custom recipe for user_id:", inferred_uid, "number:", new_id_int)
        new_recipe = _load_custom_recipe(inferred_uid, new_id_int)
        if not new_recipe:
            print("[replace-logic][ERROR] Custom recipe not found for", inferred_uid, new_id_int)
            return (
                jsonify(
                    {
                        "error": "Custom recipe not found.",
                        "details": {
                            "user_id": inferred_uid,
                            "number": new_id_int,
                        },
                    }
                ),
                400,
            )
        print("[replace-logic] Loaded custom recipe keys:", list(new_recipe.keys()))
    else:
        print("[replace-logic] Using BASE recipe branch")
        new_recipe_row = recipe_df.loc[recipe_df["number"] == new_id_int]
        print("[replace-logic] Base recipe match count:", len(new_recipe_row))
        if new_recipe_row.empty:
            print("[replace-logic][ERROR] Base recipe not found for id:", new_id_int)
            return jsonify({"error": "New recipe not found."}), 400

        new_recipe = new_recipe_row.iloc[0].to_dict()
        new_recipe = {k: (None if pd.isnull(v) else v) for k, v in new_recipe.items()}

        if new_recipe.get("meal_slot") == "Snack":
            print("[replace-logic] Base recipe is a Snack, parsing list fields")
            if isinstance(new_recipe.get("instructions"), str):
                new_recipe["instructions"] = ast.literal_eval(new_recipe["instructions"])
            if isinstance(new_recipe.get("ingredients_with_quantities"), str):
                new_recipe["ingredients_with_quantities"] = ast.literal_eval(
                    new_recipe["ingredients_with_quantities"]
                )
    
    # ---------- ensure custom recipe exists in recipe_df for nutrition logic ----------
    if source == "custom":
        # update_nutrition_values expects to find this ID in recipe_df
        # check whether it's already there (it won't be for your custom IDs like 29)
        if "number" in recipe_df.columns:
            exists = not recipe_df.loc[recipe_df["number"] == new_id_int].empty
        elif "id" in recipe_df.columns:
            exists = not recipe_df.loc[recipe_df["id"] == new_id_int].empty
        else:
            exists = False

        if not exists:
            print(f"[replace-logic] Injecting custom recipe {new_id_int} into recipe_df")

            row_for_df = {}

            for col in recipe_df.columns:
                # 1) If our custom recipe actually has this field and it's not None, use it
                if col in new_recipe and new_recipe[col] is not None:
                    row_for_df[col] = new_recipe[col]

                # 2) Ensure the key column is set
                elif col in ("number", "id"):
                    row_for_df[col] = new_id_int

                else:
                    # 3) Decide default based on dtype: numeric → 0, else None
                    col_series = recipe_df[col]
                    if pd.api.types.is_numeric_dtype(col_series.dtype):
                        row_for_df[col] = 0
                    else:
                        row_for_df[col] = None

            # Explicitly ensure energy_kcal is set if we have it on new_recipe
            if "energy_kcal" in recipe_df.columns and new_recipe.get("energy_kcal") is not None:
                row_for_df["energy_kcal"] = float(new_recipe["energy_kcal"])

            # Append to recipe_df so update_nutrition_values can find it
            recipe_df = pd.concat(
                [recipe_df, pd.DataFrame([row_for_df])],
                ignore_index=True,
            )

            # Rebuild snack_recipes_df in case this custom recipe is a snack
            if "meal_slot" in recipe_df.columns:
                snack_recipes_df = recipe_df[recipe_df["meal_slot"] == "['snack']"]

            print(
                f"[replace-logic] recipe_df now has shape: {recipe_df.shape}, "
                f"snack_recipes_df: {snack_recipes_df.shape}"
            )



    # ---------------- normalize fields expected by the frontend -----------

    new_recipe["id"] = int(new_recipe.get("number", new_id_int))
    if new_recipe.get("energy_kcal") is not None:
        new_recipe["calories"] = int(float(new_recipe["energy_kcal"]))
    else:
        new_recipe["calories"] = None
    print("[replace-logic] new_recipe id:", new_recipe["id"], "calories:", new_recipe["calories"])

    if "preptime" in new_recipe:
        new_recipe["prep_time"] = new_recipe["preptime"]
    else:
        new_recipe["prep_time"] = new_recipe.get("prep_time")
    print("[replace-logic] new_recipe prep_time:", new_recipe.get("prep_time"))

    new_recipe["meal_name"] = old_recipe.get("meal_name", new_recipe.get("meal_slot"))
    print("[replace-logic] new_recipe meal_name:", new_recipe["meal_name"])

    # ---------------- update totals + shopping list (unchanged) ----------
    print("[replace-logic] Updating nutrition values (subtract old)...")
    meal_plan = update_nutrition_values(
        meal_plan, old_recipe, "subtract", recipe_df, snack_recipes_df
    )
    print("[replace-logic] Inserting new recipe into meal_plan...")
    meal_plan["days"][day_index]["recipes"].insert(recipe_index, new_recipe)
    print("[replace-logic] Updating nutrition values (add new)...")
    meal_plan = update_nutrition_values(
        meal_plan, new_recipe, "add", recipe_df, snack_recipes_df
    )

    print("[replace-logic] Regenerating shopping list + status info...")
    time.sleep(0.1)
    meal_plan = gen_shopping_list(meal_plan)
    meal_plan = insert_status_nutrient_info(meal_plan)
    time.sleep(0.1)

    print("[replace-logic] ===== EXIT OK ===== id_replaced:", new_recipe["number"])
    return jsonify({"meal_plan": meal_plan, "id_replaced": new_recipe["number"]})
