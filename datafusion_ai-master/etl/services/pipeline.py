from django.utils import timezone
from ..models import ImportJob, ImportLog
from .extractor import extract_from_excel, extract_from_csv
from .transformer import transform_all
from .loader import load_all


def run_pipeline(job_id: int) -> bool:
    """
    Main ETL orchestrator.
    Runs Extract → Transform → Load for a given ImportJob.
    Returns True if successful, False if failed.
    """
    try:
        job = ImportJob.objects.get(id=job_id)
    except ImportJob.DoesNotExist:
        return False

    job.status     = 'running'
    job.started_at = timezone.now()
    job.save()

    _log(job, 'info', f'Pipeline started for: {job.data_source.name}')

    try:
        # ── EXTRACT ──────────────────────────────────────────────────
        file_path   = job.data_source.file.path
        source_type = job.data_source.source_type

        _log(job, 'info', f'Extracting from {source_type}: {file_path}')

        if source_type == 'excel':
            extracted = extract_from_excel(file_path)
        else:
            extracted = extract_from_csv(file_path)

        total_extracted = sum(len(df) for df in extracted.values())
        job.rows_extracted = total_extracted
        job.save()

        _log(job, 'info', f'Extracted {total_extracted} total rows.')

        # ── TRANSFORM ─────────────────────────────────────────────────
        _log(job, 'info', 'Transforming and validating data...')
        cleaned, warnings = transform_all(extracted)

        for warning in warnings:
            _log(job, 'warning', warning)

        # ── LOAD ──────────────────────────────────────────────────────
        _log(job, 'info', 'Loading data into database...')
        results = load_all(cleaned)

        total_loaded = sum(results.values())
        job.rows_loaded = total_loaded
        job.save()

        for sheet, rows in results.items():
            if rows > 0:
                _log(job, 'info', f'Loaded {rows} rows into {sheet}.')

        job.status      = 'completed'
        job.finished_at = timezone.now()
        job.save()

        _log(job, 'info', f'Pipeline completed. {total_loaded} rows loaded.')
        return True

    except Exception as e:
        job.status        = 'failed'
        job.error_message = str(e)
        job.finished_at   = timezone.now()
        job.save()
        _log(job, 'error', f'Pipeline failed: {str(e)}')
        return False


def _log(job: ImportJob, level: str, message: str):
    """Helper to create an ImportLog entry."""
    ImportLog.objects.create(job=job, level=level, message=message)