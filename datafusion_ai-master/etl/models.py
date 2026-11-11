from django.db import models
from django.contrib.auth.models import User


class DataSource(models.Model):
    SOURCE_TYPES = [
        ('excel', 'Excel File'),
        ('csv', 'CSV File'),
    ]

    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    file = models.FileField(upload_to='uploads/')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.source_type})"

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Data Source'
        verbose_name_plural = 'Data Sources'


class ImportJob(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('running',    'Running'),
        ('completed',  'Completed'),
        ('failed',     'Failed'),
    ]

    data_source = models.ForeignKey(
        DataSource, on_delete=models.CASCADE, related_name='import_jobs'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    started_at  = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    rows_extracted  = models.IntegerField(default=0)
    rows_loaded     = models.IntegerField(default=0)
    error_message   = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Job #{self.id} — {self.data_source.name} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Import Job'
        verbose_name_plural = 'Import Jobs'


class ImportLog(models.Model):
    LOG_LEVELS = [
        ('info',    'Info'),
        ('warning', 'Warning'),
        ('error',   'Error'),
    ]

    job     = models.ForeignKey(
        ImportJob, on_delete=models.CASCADE, related_name='logs'
    )
    level   = models.CharField(max_length=10, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.level.upper()}] {self.message[:60]}"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Import Log'
        verbose_name_plural = 'Import Logs'