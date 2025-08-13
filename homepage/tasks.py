import os
import zipfile
from celery import shared_task
from docx2pdf import convert  # pip install docx2pdf
from django.conf import settings
from .utils import update_job_status

OUTPUT_DIR = os.path.join(settings.BASE_DIR, "temp_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@shared_task
def process_job_task(job_id, saved_files):
    status_data = {
        "status": "IN_PROGRESS",
        "files": {os.path.basename(f).split("_", 1)[1]: "PENDING" for f in saved_files},
        "zip_path": ""
    }
    update_job_status(job_id, status_data)

    processed_files = []

    for file_path in saved_files:
        filename = os.path.basename(file_path).split("_", 1)[1]
        status_data["files"][filename] = "IN_PROGRESS"
        update_job_status(job_id, status_data)

        try:
            # PDF will be saved in the same folder as DOCX
            pdf_path = os.path.splitext(file_path)[0] + ".pdf"

            from docx2pdf import convert
            convert(file_path, pdf_path)

            if os.path.exists(pdf_path):
                # Add to processed_files list
                processed_files.append((pdf_path, os.path.basename(pdf_path)))
                status_data["files"][filename] = "COMPLETED"
            else:
                status_data["files"][filename] = "FAILED"

        except Exception as e:
            status_data["files"][filename] = f"FAILED: {str(e)}"
        
        update_job_status(job_id, status_data)

    # Create ZIP of all PDFs
    zip_path = os.path.join(OUTPUT_DIR, f"{job_id}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for full_path, name_in_zip in processed_files:
            zipf.write(full_path, arcname=name_in_zip)  # correct arcname ensures proper file inside ZIP

    status_data["status"] = "COMPLETED"
    status_data["zip_path"] = zip_path
    update_job_status(job_id, status_data)