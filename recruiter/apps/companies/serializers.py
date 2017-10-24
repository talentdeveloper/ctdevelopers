from rest_framework import serializers

from .models import (
    Company,
)
from core.serializers import ModelSerializer


class CompanySerializer(ModelSerializer):

    country = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'

    def get_country(self, obj):
        return obj.country.name
