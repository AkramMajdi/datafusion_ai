import time
from .models import PageVisit, UserSession

EXCLUDED_PATHS = [
    '/static/', '/media/', '/favicon.ico',
    '/admin/jsi18n/', '/__debug__/',
]


def get_device_type(user_agent: str) -> str:
    ua = user_agent.lower()
    if any(x in ua for x in ['mobile', 'android', 'iphone']):
        return 'mobile'
    if any(x in ua for x in ['tablet', 'ipad']):
        return 'tablet'
    return 'desktop'


def get_client_ip(request) -> str:
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class UserTrackingMiddleware:
    """
    Automatically tracks every page visit and session.
    Runs on every request — no changes needed in views.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip excluded paths
        path = request.path
        if any(path.startswith(ex) for ex in EXCLUDED_PATHS):
            return self.get_response(request)

        start_time = time.time()
        response   = self.get_response(request)
        duration   = int((time.time() - start_time) * 1000)

        # Only track GET requests and successful responses
        if request.method == 'GET' and response.status_code < 400:
            try:
                self._track_visit(request, path, duration)
                self._track_session(request)
            except Exception:
                pass

        return response

    def _track_visit(self, request, path, duration):
        user       = request.user if request.user.is_authenticated else None
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        PageVisit.objects.create(
            user             = user,
            session_key      = request.session.session_key or '',
            path             = path,
            method           = request.method,
            ip_address       = get_client_ip(request),
            user_agent       = user_agent[:500],
            device_type      = get_device_type(user_agent),
            referrer         = request.META.get('HTTP_REFERER', '')[:500],
            response_time_ms = duration,
        )

    def _track_session(self, request):
        session_key = request.session.session_key
        if not session_key:
            return

        user = request.user if request.user.is_authenticated else None

        session, created = UserSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'user'       : user,
                'ip_address' : get_client_ip(request),
                'device_type': get_device_type(
                    request.META.get('HTTP_USER_AGENT', '')
                ),
            }
        )

        # Update session stats
        session.total_pages += 1
        if user and not session.user:
            session.user = user
        session.save()