from django.contrib import admin
from .models import DataSource, ImportJob, ImportLog


class ImportLogInline(admin.TabularInline):
    model = ImportLog
    extra = 0
    readonly_fields = ('level', 'message', 'created_at')


class ImportJobInline(admin.TabularInline):
    model = ImportJob
    extra = 0
    readonly_fields = ('status', 'rows_extracted', 'rows_loaded', 'created_at')


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display  = ('name', 'source_type', 'uploaded_by', 'uploaded_at')
    list_filter   = ('source_type',)
    search_fields = ('name',)
    inlines       = [ImportJobInline]


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display  = ('id', 'data_source', 'status', 'rows_extracted',
                     'rows_loaded', 'created_at')
    list_filter   = ('status',)
    readonly_fields = ('started_at', 'finished_at', 'rows_extracted',
                       'rows_loaded', 'error_message')
    inlines       = [ImportLogInline]


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display  = ('job', 'level', 'message', 'created_at')
    list_filter   = ('level',)