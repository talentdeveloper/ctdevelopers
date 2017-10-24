import logging

from django.apps import apps
from django.contrib.gis.geoip import GeoIP
from django.dispatch import receiver

from allauth.account.signals import user_logged_in


logger = logging.getLogger('debug_log')


@receiver(user_logged_in)
def logged_in(sender, request, **kwargs):
    UserLocation = apps.get_model('users', 'UserLocation')

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    geoip = GeoIP()
    try:
        city = geoip.city(ip_address)
        user = kwargs.get('user')

        UserLocation.objects.create(
            user=user,
            ip_address=ip_address,
            country_code=city.get('country_code'),
            country_name=city.get('country_name'),
            city=city.get('city'),
            latitude=city.get('latitude'),
            longitude=city.get('longitude'),
            continent_code=city.get('continent_code')
        )
    except Exception as e:
        logger.debug(e)
