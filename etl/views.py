from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UploadFileForm
from .models import DataSource, ImportJob
from .services.pipeline import run_pipeline


@login_required
def upload_view(request):
    """Show upload form and handle file submission."""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            source          = form.save(commit=False)
            source.uploaded_by = request.user
            source.save()

            # Create a job and run pipeline immediately
            job = ImportJob.objects.create(data_source=source)
            success = run_pipeline(job.id)

            if success:
                messages.success(
                    request,
                    f'File "{source.name}" imported successfully! '
                    f'{job.rows_loaded} rows loaded.'
                )
            else:
                messages.error(
                    request,
                    f'Import failed: {job.error_message}'
                )

            return redirect('etl:job_detail', pk=job.id)
    else:
        form = UploadFileForm()

    recent_jobs = ImportJob.objects.select_related(
        'data_source'
    ).order_by('-created_at')[:10]

    return render(request, 'etl/upload.html', {
        'form'       : form,
        'recent_jobs': recent_jobs,
    })


@login_required
def job_detail_view(request, pk):
    """Show import job details and logs."""
    job  = get_object_or_404(ImportJob, pk=pk)
    logs = job.logs.all()

    return render(request, 'etl/job_detail.html', {
        'job' : job,
        'logs': logs,
    })


@login_required
def job_status_api(request, pk):
    """JSON endpoint — returns job status (for polling)."""
    job = get_object_or_404(ImportJob, pk=pk)
    return JsonResponse({
        'status'        : job.status,
        'rows_extracted': job.rows_extracted,
        'rows_loaded'   : job.rows_loaded,
        'error_message' : job.error_message,
    })


@login_required
def sources_list_view(request):
    """List all uploaded data sources."""
    sources = DataSource.objects.select_related(
        'uploaded_by'
    ).prefetch_related('import_jobs').order_by('-uploaded_at')

    return render(request, 'etl/sources.html', {
        'sources': sources,
    })