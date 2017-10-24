from django.core.cache import cache
from django.utils import timezone


def update_user_presence(user, idle=False):
    now = timezone.now()
    if not idle:
        cache.set(f'seen_{user.email}', now, None)


def update_user_idle(user, idle):
    cache.set(f'idle_{user.email}', idle, None)
