from django.db import models


class APIResponse(models.Model):
     success = models.BooleanField(default=False)
     errorMessage = models.CharField(max_length=1024, null=True)

     class Meta:
         managed = False

class Todo(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=2048, null=False)
    status = models.CharField(max_length=50, null=False)
    type = models.CharField(max_length=50, null=False)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)