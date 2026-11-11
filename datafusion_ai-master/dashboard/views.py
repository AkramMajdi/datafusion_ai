import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services.query_engine import (
    get_kpi_summary,
    get_revenue_by_month,
    get_customers_by_segment,
    get_top_campaigns,
    get_sales_by_channel,
    get_leads_by_stage,
    get_analytics_summary,
)


@login_required
def dashboard_view(request):
    """Main dashboard page."""
    kpis      = get_kpi_summary()
    analytics = get_analytics_summary()

    return render(request, 'dashboard/index.html', {
        'kpis'     : kpis,
        'analytics': analytics,
    })


@login_required
def charts_api(request):
    """JSON endpoint — returns all chart data."""
    data = {
        'revenue_by_month'    : get_revenue_by_month(),
        'customers_by_segment': get_customers_by_segment(),
        'top_campaigns'       : get_top_campaigns(),
        'sales_by_channel'    : get_sales_by_channel(),
        'leads_by_stage'      : get_leads_by_stage(),
    }
    return JsonResponse(data)