from google.cloud import storage
import json
import os
import csv
import codecs

def set_lifecycle_with_prefix(bucket, prefix, days):
    bucket.add_lifecycle_delete_rule(age=days, matches_prefix=[prefix])
    bucket.patch()

def _underscore_error_handler(exc: UnicodeDecodeError):
    return ('_' * (exc.end - exc.start), exc.end)

codecs.register_error('underscorereplace', _underscore_error_handler)

_gcs_client = None
def _get_storage_client():
    global _gcs_client
    if _gcs_client is None:
        sj = os.getenv("SERVICE_JSON")
        if sj:
            _gcs_client = storage.Client.from_service_account_info(json.loads(sj))
        else:
            _gcs_client = storage.Client()
    return _gcs_client

def set_lifecycle_with_prefix(bucket, prefix, days):
    bucket.add_lifecycle_delete_rule(age=days, matches_prefix=[prefix])
    bucket.patch()

def upload_mealplan_json_to_gcs(response_data, path):
    client = storage.Client.from_service_account_info(json.loads(os.getenv("SERVICE_JSON")))
    bucket_name = 'meal-plan-data'
    bucket = client.bucket(bucket_name)
    
    set_lifecycle_with_prefix(bucket, "meal-plans-for-user/", 7)
    blob = bucket.blob(path)
    
    blob.upload_from_string(
        data=json.dumps(response_data),
        content_type='application/json'
    )
    print(f"Meal plan file is successfully uploaded to {path}")

def download_mealplan_json_from_gcs(mealplan_path):
    print("[DEBUG] GCS Download Path:", mealplan_path)

    if not mealplan_path.endswith(".json"):
        mealplan_path += ".json"

    try:
        client = storage.Client.from_service_account_info(
            json.loads(os.getenv("SERVICE_JSON"))
        )
        bucket = client.bucket("meal-plan-data")
        blob = bucket.blob(mealplan_path)

        data = blob.download_as_string().decode("utf-8")
        return json.loads(data)

    except Exception as e:
        print(f"[ERROR] Failed to download from GCS: {e}")
        raise

def read_csv_rows_from_gcs(bucket_name: str, blob_path: str, *, encoding: str = "utf-8"):
    client = _get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    if not blob.exists():
        raise FileNotFoundError(f"GCS object not found: gs://{bucket_name}/{blob_path}")

    rows = []
    with blob.open("rt", encoding=encoding, errors="underscorereplace", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows

def read_recipe_assets_from_gcs(recipe_id: str, *,
                                bucket_name: str = "meal-plan-data",
                                base_prefix: str = "meal_db"):

    instructions_blob = f"{base_prefix}/instructions/instructions_{recipe_id}.csv"
    ingredients_blob  = f"{base_prefix}/ingredients/{recipe_id}.csv"

    instructions = read_csv_rows_from_gcs(bucket_name, instructions_blob, encoding="utf-8")
    ingredients  = read_csv_rows_from_gcs(bucket_name, ingredients_blob,  encoding="utf-8")

    return instructions, ingredients