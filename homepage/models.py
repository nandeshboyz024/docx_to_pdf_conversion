from django.db import models
import uuid
from django.contrib.postgres.fields import JSONField  # Django >= 3.1 supports JSONField natively

class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, default='PENDING')
    files = models.JSONField(default=dict)  # {"file.docx": "PENDING", ...}
    zip_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)