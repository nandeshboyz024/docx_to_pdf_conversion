import os
import zipfile
import pypandoc
import shutil
from celery import shared_task
from django.conf import settings
from homepage.models import Job  # import the Job model

OUTPUT_DIR = os.path.join(settings.BASE_DIR, "temp_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_valid_docx(file_path):
    """Basic validation for DOCX format"""
    return file_path.lower().endswith(".docx") and os.path.exists(file_path) and os.path.getsize(file_path) > 0

def has_enough_disk_space(required_mb=10):
    """Conceptual disk space check (default 10MB free space)"""
    total, used, free = shutil.disk_usage(OUTPUT_DIR)
    return free > required_mb * 1024 * 1024

def update_job_in_db(job_id, status_data):
    """Update the Job model in PostgreSQL"""
    try:
        job = Job.objects.get(id=job_id)
        job.status = status_data.get("status", job.status)
        job.files = status_data.get("files", job.files)
        job.zip_path = status_data.get("zip_path", job.zip_path)
        job.save()
    except Job.DoesNotExist:
        print(f"Job {job_id} does not exist!")

@shared_task
def process_job_task(job_id, saved_files):
    status_data = {
        "status": "IN_PROGRESS",
        "files": {os.path.basename(f).split("_", 1)[1]: "PENDING" for f in saved_files},
        "zip_path": ""
    }
    update_job_in_db(job_id, status_data)

    processed_files = []

    for file_path in saved_files:
        filename = os.path.basename(file_path).split("_", 1)[1]
        status_data["files"][filename] = "IN_PROGRESS"
        update_job_in_db(job_id, status_data)

        try:
            # Check if file is valid DOCX
            if not is_valid_docx(file_path):
                raise ValueError("Invalid or corrupted DOCX file")

            # Check disk space before processing
            if not has_enough_disk_space():
                raise OSError("Insufficient disk space")
            
            pdf_path = os.path.splitext(file_path)[0] + ".pdf"

            # Convert DOCX to PDF using pypandoc
            pypandoc.convert_file(file_path, 'pdf', outputfile=pdf_path, extra_args=['--extract-media=./temp_media'])

            if os.path.exists(pdf_path):
                processed_files.append((pdf_path, os.path.basename(pdf_path)))
                status_data["files"][filename] = "COMPLETED"
            else:
                status_data["files"][filename] = "FAILED: PDF not created"

        except Exception as e:
            status_data["files"][filename] = f"FAILED: {str(e)}"

        update_job_in_db(job_id, status_data)

    # Create ZIP of all PDFs
    zip_path = os.path.join(OUTPUT_DIR, f"{job_id}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for full_path, name_in_zip in processed_files:
            zipf.write(full_path, arcname=name_in_zip)

    status_data["status"] = "COMPLETED"
    status_data["zip_path"] = zip_path
    update_job_in_db(job_id, status_data)