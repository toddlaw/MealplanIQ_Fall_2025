import os
import pandas as pd
import glob

MEAL_DATABASE_PATH = "meal_database.csv"
CUSTOM_NUTRIENT_DIR = "custom_recipes/nutrients"

def load_meal_database_for_user(uid: str):
    """
    Loads the main meal database CSV and appends custom recipe CSVs that match
    <uid>_<number>.csv inside /custom_recipes/nutrients.

    Returns:
        pandas.DataFrame
    """
    # 1. Load main database
    base_df = pd.read_csv(MEAL_DATABASE_PATH)

    # 2. Build pattern: /custom_recipes/nutrients/<uid>_*.csv
    pattern = os.path.join(CUSTOM_NUTRIENT_DIR, f"{uid}_*.csv")

    custom_files = glob.glob(pattern)

    if not custom_files:
        print(f"No custom nutrient files found for user {uid}.")
        return base_df    # No custom recipes, return original DB

    # 3. Load & append all matching custom files
    custom_rows = []
    for file in custom_files:
        try:
            df = pd.read_csv(file)

            # Ensure DF has matching columns
            missing_cols = set(base_df.columns) - set(df.columns)
            for col in missing_cols:
                df[col] = None  # Fill missing with empty / None

            df = df[base_df.columns]   # Column order match
            custom_rows.append(df)

        except Exception as e:
            print(f"Error loading {file}: {e}")

    if custom_rows:
        custom_df = pd.concat(custom_rows, ignore_index=True)
        merged_df = pd.concat([base_df, custom_df], ignore_index=True)
        return merged_df

    return base_df