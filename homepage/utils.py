import os
import json
from django.conf import settings

JOB_META_DIR = os.path.join(settings.BASE_DIR, "job_metadata")
os.makedirs(JOB_META_DIR, exist_ok=True)

def update_job_status(job_id, status_data):
    """Save job status as JSON in a file."""
    file_path = os.path.join(JOB_META_DIR, f"{job_id}.json")
    with open(file_path, "w") as f:
        json.dump(status_data, f)

def get_job_status(job_id):
    """Load job status from file."""
    file_path = os.path.join(JOB_META_DIR, f"{job_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None