from .models import Job

def update_job_status(job_id, status_data):
    try:
        job, _ = Job.objects.get_or_create(id=job_id)
        job.status = status_data.get("status", job.status)
        job.files = status_data.get("files", job.files)
        job.zip_path = status_data.get("zip_path", job.zip_path)
        job.save()
    except Exception as e:
        print(f"Error updating job {job_id}: {e}")

def get_job_status(job_id):
    try:
        job = Job.objects.get(id=job_id)
        return {
            "status": job.status,
            "files": job.files,
            "zip_path": job.zip_path
        }
    except Job.DoesNotExist:
        return None