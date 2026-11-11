from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services.analyzer import (
    get_behavior_summary,
    get_top_pages,
    get_visits_by_hour,
    get_visits_by_day,
    get_device_breakdown,
    get_most_active_users,
    get_recent_visits,
)


@login_required
def analytics_view(request):
    """Full behavior analytics page."""
    summary      = get_behavior_summary()
    top_pages    = get_top_pages(10)
    active_users = get_most_active_users(10)
    recent       = get_recent_visits(20)

    return render(request, 'core/analytics.html', {
        'summary'     : summary,
        'top_pages'   : top_pages,
        'active_users': active_users,
        'recent'      : recent,
    })


@login_required
def analytics_api(request):
    """JSON endpoint for analytics charts."""
    data = {
        'visits_by_hour': get_visits_by_hour(),
        'visits_by_day' : get_visits_by_day(),
        'device_breakdown': get_device_breakdown(),
    }
    return JsonResponse(data)