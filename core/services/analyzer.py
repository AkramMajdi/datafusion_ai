from django.db import connection
from django.contrib.auth.models import User
from ..models import PageVisit, UserSession


def get_behavior_summary():
    """Top-level numbers for the dashboard summary cards."""
    total_visits   = PageVisit.objects.count()
    total_sessions = UserSession.objects.count()
    active_users   = PageVisit.objects.values(
        'user').distinct().count()
    avg_pages = 0
    if total_sessions > 0:
        avg_pages = round(
            UserSession.objects.all().values_list(
                'total_pages', flat=True
            ).count() / total_sessions, 1
        )
    return {
        'total_visits'  : total_visits,
        'total_sessions': total_sessions,
        'active_users'  : active_users,
        'avg_pages'     : avg_pages,
    }


def get_top_pages(limit=10):
    """Most visited pages."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT path, COUNT(*) as visits
            FROM core_pagevisit
            GROUP BY path
            ORDER BY visits DESC
            LIMIT %s
        """, [limit])
        rows = cursor.fetchall()
    return [{'path': r[0], 'visits': r[1]} for r in rows]


def get_visits_by_hour():
    """Visit count grouped by hour of day (0-23)."""
    counts = [0] * 24
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                CAST(STRFTIME('%H', visited_at) AS INTEGER) as hour,
                COUNT(*) as visits
            FROM core_pagevisit
            GROUP BY hour
            ORDER BY hour
        """)
        for row in cursor.fetchall():
            if 0 <= row[0] <= 23:
                counts[row[0]] = row[1]
    return {
        'labels': [f"{h:02d}:00" for h in range(24)],
        'data'  : counts,
    }


def get_visits_by_day():
    """Visit count for last 30 days."""
    labels = []
    data   = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE(visited_at) as day,
                COUNT(*) as visits
            FROM core_pagevisit
            WHERE visited_at >= DATE('now', '-30 days')
            GROUP BY day
            ORDER BY day ASC
        """)
        for row in cursor.fetchall():
            labels.append(str(row[0]))
            data.append(int(row[1]))
    return {'labels': labels, 'data': data}


def get_device_breakdown():
    """Visits split by device type."""
    labels = []
    data   = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT device_type, COUNT(*) as total
            FROM core_pagevisit
            GROUP BY device_type
            ORDER BY total DESC
        """)
        for row in cursor.fetchall():
            labels.append(str(row[0]).title())
            data.append(int(row[1]))
    return {'labels': labels, 'data': data}


def get_most_active_users(limit=10):
    """Users with most page visits."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                u.username,
                COUNT(pv.id) as visits,
                MAX(pv.visited_at) as last_seen
            FROM core_pagevisit pv
            JOIN auth_user u ON pv.user_id = u.id
            GROUP BY u.username
            ORDER BY visits DESC
            LIMIT %s
        """, [limit])
        rows = cursor.fetchall()
    return [
        {'username': r[0], 'visits': r[1], 'last_seen': r[2]}
        for r in rows
    ]


def get_recent_visits(limit=20):
    """Latest page visits for the live feed."""
    return PageVisit.objects.select_related('user').order_by(
        '-visited_at'
    )[:limit]