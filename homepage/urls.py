from . import views
from django.urls import path
urlpatterns = [
    path("home-page",views.myPage,name="home_page"),
    path("api/v1/jobs",views.submit_job,name="submit_job"),
    path("api/v1/jobs/<str:job_id>",views.job_status,name="get_job_status"),
    path("api/v1/jobs/<str:job_id>/download",views.download_zip,name="download_zip"),
]
