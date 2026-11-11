from django.db import models
from django.contrib.auth.models import User


class PageVisit(models.Model):
    user         = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='page_visits'
    )
    session_key  = models.CharField(max_length=100, blank=True)
    path         = models.CharField(max_length=500)
    method       = models.CharField(max_length=10, default='GET')
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    user_agent   = models.CharField(max_length=500, blank=True)
    device_type  = models.CharField(max_length=20, default='desktop')
    referrer     = models.CharField(max_length=500, blank=True)
    visited_at   = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.IntegerField(default=0)

    def __str__(self):
        user = self.user.username if self.user else 'Anonymous'
        return f"{user} → {self.path} ({self.visited_at:%Y-%m-%d %H:%M})"

    class Meta:
        ordering = ['-visited_at']
        verbose_name = 'Page Visit'
        verbose_name_plural = 'Page Visits'


class UserSession(models.Model):
    user             = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sessions'
    )
    session_key      = models.CharField(max_length=100, unique=True)
    ip_address       = models.GenericIPAddressField(null=True, blank=True)
    device_type      = models.CharField(max_length=20, default='desktop')
    started_at       = models.DateTimeField(auto_now_add=True)
    last_activity    = models.DateTimeField(auto_now=True)
    total_pages      = models.IntegerField(default=0)
    duration_seconds = models.IntegerField(default=0)
    is_active        = models.BooleanField(default=True)

    def __str__(self):
        user = self.user.username if self.user else 'Anonymous'
        return f"{user} — session {self.session_key[:8]} ({self.total_pages} pages)"

    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'