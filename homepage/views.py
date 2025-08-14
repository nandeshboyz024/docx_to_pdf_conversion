import os
from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .tasks import process_job_task
from homepage.models import Job  # Import Job model
import uuid

UPLOAD_DIR = os.path.join(settings.BASE_DIR, "temp_uploads")
OUTPUT_DIR = os.path.join(settings.BASE_DIR, "temp_outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@csrf_exempt
@require_POST
def submit_job(request):
    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({"error": "No files uploaded"}, status=400)

    job_id = str(uuid.uuid4())
    # Create Job entry in PostgreSQL
    job = Job.objects.create(
        id=job_id,
        status="PENDING",
        files={file.name: "PENDING" for file in files},
        zip_path=""
    )

    saved_files = []
    for file in files:
        temp_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.name}")
        with open(temp_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
        saved_files.append(temp_path)

    # Send job to Celery worker
    process_job_task.delay(job_id, saved_files)

    return JsonResponse({"job_id": job_id, "status": job.status})


def job_status(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

    response = {
        "job_id": job_id,
        "status": job.status,
        "files": job.files
    }

    if job.status == "COMPLETED":
        response["download_url"] = f"/download/{job_id}/"

    return JsonResponse(response)


def download_zip(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

    if job.status != "COMPLETED":
        return JsonResponse({"error": "File not ready"}, status=404)

    zip_path = job.zip_path
    if not os.path.exists(zip_path):
        return JsonResponse({"error": "File not found"}, status=404)

    return FileResponse(open(zip_path, 'rb'), as_attachment=True, filename=f"{job_id}.zip")


def myPage(request):
    return render(request,'home.html')