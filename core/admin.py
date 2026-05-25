from django.contrib import admin
from .models import PageVisit, UserSession


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display  = ('user', 'path', 'device_type',
                     'response_time_ms', 'visited_at')
    list_filter   = ('device_type', 'method')
    search_fields = ('path', 'user__username', 'ip_address')
    readonly_fields = ('visited_at',)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'session_key', 'device_type',
                     'total_pages', 'duration_seconds', 'last_activity')
    list_filter   = ('device_type', 'is_active')
    search_fields = ('user__username', 'ip_address')