from django.db.models.functions import Lower

from django_countries import countries as django_countries
from rest_framework.serializers import (
    ModelSerializer as BaseModelSerializer,
    Serializer as BaseSerializer,
    SerializerMethodField,
)


class DynamicSerializerMixin(object):
    def apply_include_fields(self, fields=None):
        if not fields:
            return

        # drop fields that are not specified in the `fields` argument
        fields = set(self.fields.keys()) - set(fields)

        for field in fields:
            self.fields.pop(field)


    def apply_exclude_fields(self, fields=None):
        if not fields:
            return

        # drop fields that are only within the `fields` property
        fields = set(self.fields.keys()) & set(fields)

        for field in fields:
            self.fields.pop(field)


class ModelSerializer(BaseModelSerializer, DynamicSerializerMixin):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        super(ModelSerializer, self).__init__(*args, **kwargs)

        self.apply_include_fields(fields)
        self.apply_exclude_fields(exclude)


class Serializer(BaseSerializer, DynamicSerializerMixin):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        super (Serializer, self).__init__(*args, **kwargs)

        self.apply_include_fields(fields)
        self.apply_exclude_fields(exclude)


class LocationSerializer(Serializer):

    cities = SerializerMethodField()
    countries = SerializerMethodField()

    def get_cities(self, obj):
        return obj.annotate(lower_city=Lower('city')) \
            .distinct('lower_city') \
            .values_list('lower_city', flat=True)

    def get_countries(self, obj):
        countries = obj.distinct('country').values_list('country', flat=True)
        countries = [
            {
                'code': country,
                'name': dict(django_countries).get(country),
            }
            for country in countries
            if dict(django_countries).get(country)
        ]

        return countries
