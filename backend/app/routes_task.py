# # app/routes_tasks.py
# import json
# from flask import Blueprint, request, jsonify, current_app, abort
# from google.cloud import storage
# import google.auth
# from datetime import datetime
# from zoneinfo import ZoneInfo

# from app.utils.time_utils import pt_midnight_utc_ms, get_week_range
# from app.manage_user_data import create_data_input_for_auto_gen_meal_plan
# from app.generate_meal_plan import gen_meal_plan
# from app.mealplan_service import upload_mealplan_json_to_gcs, download_mealplan_json_from_gcs
# from app.send_email import create_and_send_maizzle_email, create_and_send_maizzle_daily_email_test
# import os 
# from user_db.user_db import instantiate_database

# import requests
# import os, json

# def whoami_log():
#     creds, project = google.auth.default()
#     print(f"[WHOAMI] project={project}, sa(creds)={getattr(creds, 'service_account_email', None)}")

#     try:
#         r = requests.get(
#             "http://metadata/computeMetadata/v1/instance/service-accounts/default/email",
#             headers={"Metadata-Flavor":"Google"}, timeout=2
#         )
#         print(f"[WHOAMI] sa(metadata)={r.text if r.ok else None}")
#     except Exception as e:
#         print(f"[WHOAMI] metadata error: {e}")

#     gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#     print(f"[WHOAMI] GOOGLE_APPLICATION_CREDENTIALS={gac}")

#     sj = os.getenv("SERVICE_JSON_PATH")
#     if sj and os.path.exists(sj):
#         with open(sj) as f:
#             client_email = json.load(f).get("client_email")
#         print(f"[WHOAMI] SERVICE_JSON client_email={client_email}")


# PT = ZoneInfo("America/Los_Angeles")

# # This is python blueprint which is registered in main app so that the routes in this file can be used
# tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="")

# # Google cloud task always add head(X-AppEngine-TaskName), so make sure to check it whether it is in the request for security purpose
# def _is_task_request(req) -> bool:
#     return "X-AppEngine-TaskName" in req.headers or "X-Appengine-Taskname" in req.headers

# def _project_id() -> str:
#     return os.getenv("GCP_PROJECT")

# def _pt_midnight_from_iso(date_str: str) -> datetime:
#     # 'YYYY-MM-DD' → PT 00:00:00 datetime
#     y, m, d = map(int, date_str.split("-"))
#     return datetime(y, m, d, 0, 0, 0, tzinfo=PT)

# # put each user in enqueue => simply saying not handling users at once
# @tasks_bp.route("/cron/fanout-weekly", methods=["GET", "POST"])
# def cron_fanout_weekly():
#     print("[DEBUG] /cron/fanout-weekly hit")
#     print("[DEBUG] Headers:", dict(request.headers))
#     print("[DEBUG] Method:", request.method)
#     print("[DEBUG] Data:", request.get_data())
#     whoami_log()

#     creds, project = google.auth.default()
#     print(getattr(creds, "service_account_email", None))

#     db = instantiate_database()
#     user_ids = db.get_all_subscribed_users()
#     print("all subscribed users are retrieved", user_ids)
#     if not user_ids:
#         return jsonify({"status": "skip", "reason": "no subscribed users exist"}), 200
    
#     dates = get_week_range()
#     start_str = dates["start_str"] 
#     end_str   = dates["end_str"]

#     client = tasks_v2.CloudTasksClient()
#     parent = os.getenv("WEEKLY_QUEUE_ID")

#     enq_ok, enq_fail = 0, []
#     for uid in user_ids:
#         try:
#             payload = {"user_id": uid, "start_str": start_str, "end_str": end_str}
#             task = {
#                 "app_engine_http_request": {
#                     "http_method": tasks_v2.HttpMethod.POST,
#                     "relative_uri": "/tasks/send-weekly",
#                     "headers": {"Content-Type": "application/json"},
#                     "body": json.dumps(payload).encode("utf-8"),
#                 }
#             }
#             client.create_task(request={"parent": parent, "task": task})
#             enq_ok += 1
#         except Exception as e:
#             print(f"[ENQUEUE][ERROR] uid={uid} err={e}", flush=True)
#             enq_fail.append({"uid": uid, "error": str(e)})

#     return jsonify({
#     "status": "partial" if enq_fail else "enqueued",
#     "count_total": len(user_ids),
#     "count_enqueued": enq_ok,
#     "count_failed": len(enq_fail),
#     "failed": enq_fail,
#     "start_date": start_str,
#     "end_date": end_str
#     }), 207 if enq_fail else 200


# @tasks_bp.route("/tasks/send-weekly", methods=["POST"])
# def task_send_weekly():
#     print("[HIT] /tasks/send-weekly")
#     if not _is_task_request(request):
#         abort(403)

#     data = request.get_json(silent=True) or {}
#     print("[DEBUG] payload", data)

#     user_id   = data.get("user_id")
#     start_str = data.get("start_str")
#     end_str   = data.get("end_str")

#     if not (user_id and start_str and end_str):
#         return jsonify({"status": "skip", "reason": "invalid payload"}), 200
    
#     db = instantiate_database()

#     s_dt = _pt_midnight_from_iso(start_str)  # 'YYYY-MM-DD' -> PT 00:00 datetime
#     e_dt = _pt_midnight_from_iso(end_str)

#     bucket_name = 'meal-plan-data'
    
#     try:
#         gcs_path = f"meal-plans-for-user/{user_id}/{start_str}_to_{end_str}.json"
#         sc = storage.Client()
        
#         # bucket is object storage, so each file is an object(blob)
#         if sc.bucket(bucket_name).blob(gcs_path).exists():
#             return jsonify({"status": "skip", "reason": "already exists", "path": gcs_path}), 200
       
#         input_data = create_data_input_for_auto_gen_meal_plan(db, user_id, s_dt, e_dt)
#         print("[DEBUG] input_data", input_data)
        
#         input_data["minDate"] = pt_midnight_utc_ms(s_dt.date())
#         input_data["maxDate"] = pt_midnight_utc_ms(e_dt.date())

#         response = gen_meal_plan(input_data)

#         db.insert_user_meal_plan(user_id, response, s_dt, e_dt)

#         upload_mealplan_json_to_gcs(response, gcs_path)

#         user_name  = db.retrieve_user_name(user_id)
#         user_email = db.retrieve_user_email(user_id)
#         response = create_and_send_maizzle_email(response, user_email, user_name, start_str, end_str)

#         return jsonify({"status": "success", "user_id": user_id, "path": gcs_path}), 200
    
#     except Exception as ex:
#         return jsonify({"status": "error", "user_id": user_id, "msg": str(ex), "input data": input_data}), 500