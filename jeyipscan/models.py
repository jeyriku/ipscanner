from django.db import models

# Create your models here.

class ScanHistory(models.Model):
    network = models.CharField(max_length=255)
    scan_date = models.DateTimeField(auto_now_add=True)
    results_file = models.FileField(upload_to='scans/')
