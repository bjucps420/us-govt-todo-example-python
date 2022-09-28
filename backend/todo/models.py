from django.db import models


class Todo(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=2048, null=False)
    status = models.CharField(max_length=50, null=False)
    type = models.CharField(max_length=50, null=False)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)