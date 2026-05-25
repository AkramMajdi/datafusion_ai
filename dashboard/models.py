from django.db import models
from django.contrib.auth.models import User


class SavedFilter(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    name        = models.CharField(max_length=100)
    filters     = models.JSONField(default=dict)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.name}"

    class Meta:
        ordering = ['-created_at']


class DashboardWidget(models.Model):
    WIDGET_TYPES = [
        ('kpi',     'KPI Card'),
        ('line',    'Line Chart'),
        ('bar',     'Bar Chart'),
        ('pie',     'Pie Chart'),
        ('table',   'Data Table'),
    ]

    name         = models.CharField(max_length=100)
    widget_type  = models.CharField(max_length=20, choices=WIDGET_TYPES)
    query_key    = models.CharField(max_length=100)
    is_active    = models.BooleanField(default=True)
    order        = models.IntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.widget_type})"

    class Meta:
        ordering = ['order']