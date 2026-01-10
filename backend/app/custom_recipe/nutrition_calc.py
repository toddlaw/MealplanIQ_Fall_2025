# custom_recipe/nutrition_calc.py
import re
import math
import pandas as pd
from pathlib import Path

from .ingredient_reader import (
    load_lookup_table, load_merged_ingredients, load_blank_units,
    load_densities, load_special_units, weight_from_volume,
    scale_nutrients_per100, to_grams
)

BASE = Path(__file__).resolve().parent

LOOKUP_PATH        = BASE / "ingredient_lookup_table.csv"
MERGED_PATH        = BASE / "merged_ingredients.csv"
BLANK_UNITS_PATH   = BASE / "blank_units_items_weight_per_item.csv"
DENSITIES_PATH     = BASE / "volume_ingredients_plus_densities.csv"
SPECIAL_UNITS_PATH = BASE / "special_unit_ingredients.csv"

lookup   = load_lookup_table(str(LOOKUP_PATH))
merged   = load_merged_ingredients(str(MERGED_PATH))
blankL   = load_blank_units(str(BLANK_UNITS_PATH))
densL    = load_densities(str(DENSITIES_PATH))
specialL = load_special_units(str(SPECIAL_UNITS_PATH))

def _finite_or_zero(x):
    try:
        f = float(x)
    except Exception:
        return 0.0
    if math.isnan(f) or math.isinf(f):
        return 0.0
    return f

def _safe_num(x):
    if x is None: return 0.0
    if isinstance(x, float) and (math.isnan(x) or pd.isna(x)): return 0.0
    try: return float(x)
    except Exception: return 0.0

def parse_quantity(value) -> float:
    s = str(value or "").strip()
    if not s:
        return 0.0

    m = re.match(r'^(\d+)\s+(\d+)\/(\d+)$', s)   # "1 1/2"
    if m:
        return float(m.group(1)) + float(m.group(2)) / float(m.group(3))

    m = re.match(r'^(\d+)\/(\d+)$', s)           # "1/2"
    if m:
        return float(m.group(1)) / float(m.group(2))

    # "2.5", "2 tbsp" 같은 케이스
    try:
        cleaned = re.sub(r'[^0-9.\-]', '', s)
        return float(cleaned) if cleaned else 0.0
    except Exception:
        return 0.0

def extract_ingredients_for_calc(raw_list):
    """
    raw_list: [{name, quantity, unit, ...}]  (quantity는 string일 수도 있음)
    return:   [{name, quantity(float), unit}]
    """
    out = []
    for item in (raw_list or []):
        out.append({
            "name": str(item.get("name", "")).strip(),
            "quantity": parse_quantity(item.get("quantity")),
            "unit": str(item.get("unit", "")).strip(),
        })
    return out

def calc_nutrition(ingredients):
    """
    ingredients: [{name, quantity, unit}]
    return: {totals: {...}, per_ingredient: [...]}
    """
    totals = {}
    per_ing = []

    for ing in ingredients:
        name = (ing.get("name") or "").strip().lower()
        unit = (ing.get("unit") or "").strip().lower()
        qty  = _safe_num(ing.get("quantity"))

        code = lookup.get(name)
        nutrients_100 = merged.get(code) if code else None

        weight_g = 0.0
        scaled = {}

        if unit == "" or unit == "quantity":
            gpi = blankL.get(name)
            if gpi and nutrients_100:
                weight_g = qty * gpi
                scaled = scale_nutrients_per100(nutrients_100, weight_g)

        if not scaled:
            gpu = specialL.get((name, unit))
            if gpu and nutrients_100:
                weight_g = qty * gpu
                scaled = scale_nutrients_per100(nutrients_100, weight_g)

        if not scaled:
            weight_g = weight_from_volume(name, qty, unit, densL)
            if weight_g > 0 and nutrients_100:
                scaled = scale_nutrients_per100(nutrients_100, weight_g)

        if not scaled:
            weight_g = to_grams(qty, unit)
            if weight_g > 0 and nutrients_100:
                scaled = scale_nutrients_per100(nutrients_100, weight_g)

        for k, v in (scaled or {}).items():
            totals[k] = _finite_or_zero(totals.get(k, 0.0)) + _finite_or_zero(v)

        per_ing.append({
            "name": name,
            "qty": _finite_or_zero(qty),
            "unit": unit,
            "code": code,
            "weight_g": _finite_or_zero(weight_g),
            "nutrients": {k: _finite_or_zero(v) for k, v in (scaled or {}).items()}
        })

    totals_clean = {k: _finite_or_zero(v) for k, v in totals.items()}
    return {"totals": totals_clean, "per_ingredient": per_ing}
