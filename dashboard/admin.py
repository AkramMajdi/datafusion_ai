from django.contrib import admin
from .models import SavedFilter, DashboardWidget


@admin.register(SavedFilter)
class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at')


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'widget_type', 'query_key', 'is_active', 'order')