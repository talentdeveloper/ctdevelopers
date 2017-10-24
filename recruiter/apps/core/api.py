from django.db.models.functions import Lower

from rest_framework import (
    viewsets,
)
from rest_framework.decorators import (
    detail_route,
    list_route,
)
from rest_framework.response import Response

from recruit.models import (
    Skill,
)
from recruit.serializers import SkillSerializer


class CoreViewSet(viewsets.ViewSet):

    # GET /skills/
    @list_route(methods=['get'], url_path='skills')
    def list_skills(self, request):
        skills = Skill.objects.all() \
            .annotate(lower_name=Lower('name')) \
            .distinct('lower_name')
        return Response(SkillSerializer(skills, many=True).data)
