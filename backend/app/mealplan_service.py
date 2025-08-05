from google.cloud import storage
import json
import os

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
