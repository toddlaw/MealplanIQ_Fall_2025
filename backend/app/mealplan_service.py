from google.cloud import storage
import json
import os

def upload_mealplan_json_to_gcs(response_data, path):
    client = storage.Client.from_service_account_info(json.loads(os.getenv("SERVICE_JSON")))
    bucket_name = 'meal-plan-data'
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(path)
    
    blob.upload_from_string(
        data=json.dumps(response_data),
        content_type='application/json'
    )
    print(f"Meal plan file is successfully uploaded to {path}")
    