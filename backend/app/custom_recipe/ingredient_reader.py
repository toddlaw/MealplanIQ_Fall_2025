import csv
from typing import Dict, List, Tuple, Any
import pandas as pd


# ==============================
# CSV READERS
# ==============================

def read_name_qty_unit(csv_path: str) -> List[Dict[str, Any]]:
    """
    Read name, quantity, unit from the first CSV (cols 1..3). Skips header.
    Unit may be an empty string.
    """
    rows: List[Dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        next(r, None)  # skip header
        for row in r:
            if not row:
                continue
            name = row[0].strip().strip('"')
            qty = _parse_quantity(row[1]) if len(row) > 1 else 0.0
            unit = row[2].strip() if len(row) > 2 else ""
            rows.append({"name": name, "qty": qty, "unit": unit})
    return rows


def read_ingredient_names(csv_path: str) -> List[str]:
    """
    Read only ingredient names (first column). Skips header. Lowercases.
    """
    names: List[str] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            if row:
                names.append(row[0].strip().strip('"').lower())
    return names


def read_names_and_units(csv_path: str) -> List[Tuple[str, str]]:
    """
    Read (name, unit) pairs from the CSV.
    Uses col1 = name, col3 = unit. Skips header.
    """
    rows: List[Tuple[str, str]] = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f)
        next(r, None)  # discard header
        for row in r:
            if not row:
                continue
            name = row[0].strip().strip('"')
            unit = row[2].strip() if len(row) >= 3 else ""
            rows.append((name, unit))
    return rows


# ==============================
# LOOKUP LOADERS
# ==============================

def load_lookup_table(path: str) -> Dict[str, str]:
    """
    Load lookup mapping normalized name -> ingredient_id (as string).
    Works with either CSV (UTF-8, comma-delimited) or Excel.
    Prefers columns 'Original Name from Recipes' and 'ingredient_id'.
    """
    # Pick reader by extension
    ext = path.lower().rsplit(".", 1)[-1]
    if ext in ("xlsx", "xls"):
        df = pd.read_excel(path)
    else:
        # robust CSV reader for UTF-8 CSVs; tolerates minor issues
        df = _read_csv_robust(path)

    name_col = "Original Name from Recipes" if "Original Name from Recipes" in df.columns else df.columns[0]
    code_col = "ingredient_id" if "ingredient_id" in df.columns else df.columns[3]

    lookup: Dict[str, str] = {}
    for _, row in df.iterrows():
        name_raw = row.get(name_col)
        code_raw = row.get(code_col)
        if pd.isna(name_raw) or pd.isna(code_raw):
            continue

        name = str(name_raw).strip().strip('"').lower()
        # keep codes numeric-looking as ints, otherwise as strings
        try:
            code = str(int(str(code_raw).strip()))
        except Exception:
            code = str(code_raw).strip()

        if name:
            lookup[name] = code
    return lookup


def load_special_units(csv_path: str) -> dict[tuple, float]:
    """
    CSV schema:
      ingredient, special_unit (may contain multiple aliases), special_unit_weight_g
    Example unit cell:  \"\"\"clove\"\", \"\"cloves\"\"  (doubled quotes in the CSV)
    Returns: {(ingredient_lower, unit_lower): grams_per_unit}
    """
    df = _read_csv_robust(csv_path)
    name_col, unit_col, grams_col = df.columns[:3]

    def _aliases(cell) -> list[str]:
        if pd.isna(cell):
            return []
        t = str(cell).strip()
        # collapse doubled quotes then strip outer quotes
        t = t.replace('""', '"').strip('"')
        t = t.replace(" and ", ",")
        parts = [p.strip().strip('"').lower() for p in t.split(",") if p.strip()]
        out = []
        for u in parts:
            out.append(u)
            if u.endswith("s"):
                out.append(u[:-1])  # plural->singular
        # de-duplicate preserving order
        return list(dict.fromkeys(out))

    lut: dict[tuple, float] = {}
    for _, r in df.iterrows():
        n = str(r[name_col]).strip().strip('"').lower()
        g = pd.to_numeric(str(r[grams_col]).replace(",", "").strip(), errors="coerce")
        if not n or pd.isna(g):
            continue
        for u in _aliases(r[unit_col]):
            if u:
                lut[(n, u)] = float(g)
    return lut



def load_merged_ingredients(csv_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load merged_ingredients.csv into a dict:
    { ingredient_code: { nutrient_name: value, ... } }
    """
    df = pd.read_csv(csv_path)
    code_col = df.columns[0]
    df[code_col] = df[code_col].astype(str).str.strip()

    merged: Dict[str, Dict[str, Any]] = {}
    for _, row in df.iterrows():
        code = str(row[code_col])
        nutrients = row.to_dict()
        nutrients.pop(code_col, None)
        merged[code] = nutrients
    return merged


def load_blank_units(csv_path: str) -> Dict[str, float]:
    """
    Load blank_units_weight_per_item CSV with columns:
    ingredient, approx_weight_grams  -> { ingredient_lower: grams_per_item }
    """
    df = pd.read_csv(csv_path)
    name_col = df.columns[0]
    grams_col = df.columns[1]

    lut: Dict[str, float] = {}
    for _, r in df.iterrows():
        n = str(r[name_col]).strip().strip('"').lower()
        g_raw = str(r[grams_col]).replace(",", "").strip()  # handle "1,200"
        g = pd.to_numeric(g_raw, errors="coerce")           # NaN for text like "not necessary"
        if not n or pd.isna(g):
            continue
        lut[n] = float(g)
    return lut


def load_densities(csv_path: str) -> Dict[str, float]:
    """
    Load volume densities CSV where col0=name, col1=density_g_per_ml.
    Returns { ingredient_lower: g/ml }.
    """
    df = _read_csv_robust(csv_path)
    name_col = df.columns[0]
    dens_col = df.columns[1]

    lut: Dict[str, float] = {}
    for _, r in df.iterrows():
        n = str(r[name_col]).strip().strip('"').lower()
        d = pd.to_numeric(str(r[dens_col]).strip(), errors="coerce")
        if n and not pd.isna(d):
            lut[n] = float(d)
    return lut


# ==============================
# CONVERSIONS AND SCALING
# ==============================

def scale_nutrients_per100(nutrients_dict: Dict[str, Any], weight_g: float) -> Dict[str, float]:
    """
    Scale per-100g nutrient values by weight_g/100.
    Non-numeric fields are skipped.
    """
    factor = weight_g / 100.0
    out: Dict[str, float] = {}
    for k, v in nutrients_dict.items():
        try:
            out[k] = float(v) * factor
        except Exception:
            pass  # skip non-numeric
    return out


_UNIT_TO_ML: Dict[str, float] = {
    "tsp": 5, "teaspoon": 5, "teaspoons": 5,
    "tbsp": 15, "tablespoon": 15, "tablespoons": 15,
    "cup": 240, "cups": 240,
    "ml": 1, "milliliter": 1, "milliliters": 1,
    "l": 1000, "liter": 1000, "liters": 1000,
    "gallon": 3785,
}


def to_ml(qty: float, unit: str) -> float:
    """Convert qty of unit to milliliters. Unknown units -> 0."""
    u = (unit or "").strip().lower()
    return qty * _UNIT_TO_ML.get(u, 0.0)


def weight_from_volume(name: str, qty: float, unit: str, densities: Dict[str, float]) -> float:
    """
    Compute grams for a volume-measured ingredient:
    grams = density(g/ml) * ml  (0 if unit unknown or density missing)
    """
    ml = to_ml(qty, unit)
    if ml <= 0:
        return 0.0
    dens = densities.get(name.strip().strip('"').lower())
    if dens is None:
        return 0.0
    return dens * ml


# ==============================
# HELPERS
# ==============================

_UNIT_TO_G = {
    "g": 1, "gram": 1, "grams": 1,
    "kg": 1000, "kilogram": 1000, "kilograms": 1000,
    "oz": 28.349523125, "ounce": 28.349523125, "ounces": 28.349523125,
    "lb": 453.59237, "pound": 453.59237, "pounds": 453.59237,
}
def to_grams(qty: float, unit: str) -> float:
    u = (unit or "").strip().lower()
    return qty * _UNIT_TO_G.get(u, 0.0)


def _parse_quantity(s: str) -> float:
    """
    Parse quantities like '2', '2.5', '1/2', '2 1/2', '1-1/2', and unicode ½ ¼ ¾.
    """
    if s is None:
        return 0.0
    t = str(s).strip()
    if not t:
        return 0.0

    # map common unicode fractions to ascii
    frac_map = {
        "½": "1/2", "¼": "1/4", "¾": "3/4",
        "⅓": "1/3", "⅔": "2/3",
        "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5",
        "⅙": "1/6", "⅚": "5/6",
        "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
    }
    for u, f in frac_map.items():
        t = t.replace(u, f" {f}")

    t = t.replace("-", " ")  # handle '1-1/2'
    total = 0.0
    for part in t.split():
        if "/" in part:
            a, b = part.split("/", 1)
            try:
                total += float(a) / float(b)
            except ValueError:
                pass
        else:
            try:
                total += float(part)
            except ValueError:
                pass
    return total


def _read_csv_robust(path: str) -> pd.DataFrame:
    """
    Read CSV with fallback encodings and line skipping for messy files.
    """
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc, engine="python", on_bad_lines="skip")
        except UnicodeDecodeError:
            continue
    # last resort: ignore undecodable bytes
    return pd.read_csv(path, encoding="utf-8", engine="python",
                       on_bad_lines="skip", encoding_errors="ignore")
