from datetime import timedelta as td

from dateutil.parser import parse
from django.conf import settings
from django.utils import timezone

from ..models import UserProfile


def last_user_activity_middleware(get_response):

    def middleware(request):

        response = get_response(request)

        key = "last-activity"

        if request.user.is_authenticated:

            last_activity = request.session.get(key)

            # If key is old enough, update database.
            too_old_time = timezone.now() - td(seconds=settings.LAST_ACTIVITY_INTERVAL_SECS)
            if not last_activity or parse(last_activity) < too_old_time:
                UserProfile.objects.filter(user=request.user.pk).update(last_seen=timezone.now())

            request.session[key] = timezone.now().isoformat()

        return response

    return middleware
