from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.serializers import ModelSerializer
from recruit.models import (
    Connection,
    JobApplication,
    JobInterest,
    JobPost,
    JobReferral,
    Skill,
)
from users.serializers import (
    CandidateSerializer,
    AgentSerializer,
)


class SkillSerializer(ModelSerializer):

    class Meta:
        model = Skill
        fields = '__all__'


class JobPostSerializer(ModelSerializer):

    skills = SkillSerializer(many=True)
    posted_by = AgentSerializer()
    country = serializers.SerializerMethodField()

    class Meta:
        model = JobPost
        fields = '__all__'

    def get_country(self, obj):
        return obj.country.name


class JobApplicationSerializer(ModelSerializer):

    class Meta:
        model = JobApplication
        fields = '__all__'

    def validate(self, data):
        # check if job application already exists
        application = JobApplication.objects.filter(
            job_post=data.get('job_post'),
            candidate=data.get('candidate')
        )
        if application.exists():
            raise serializers.ValidationError(_('You have already applied for this job.'))

        return data


class JobReferralSerializer(ModelSerializer):

    class Meta:
        model = JobReferral
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(JobReferralSerializer, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial')
        self.candidate = initial.get('candidate')

    def validate_referred_to(self, data):
        if self.candidate == data:
            raise serializers.ValidationError(_('You cannot refer a job to yourself.'))

        return data

    def validate(self, data):
        referred_to = data.get('referred_to')
        referred_by = data.get('referred_by')

        # check if users are connected
        connection = Connection.objects.filter(
            (Q(connecter=referred_to.user) & Q(connectee=referred_by.user)) |
            (Q(connecter=referred_by.user) & Q(connectee=referred_to.user))
        )
        if not connection.exists():
            raise serializers.ValidationError(_('You cannot refer a job to non-connected users.'))

        # check if job referral already exists
        application = JobReferral.objects.filter(
            job_post=data.get('job_post'),
            referred_by=referred_by,
            referred_to=referred_to
        )
        if application.exists():
            raise serializers.ValidationError(_('You have already referred this job to this user.'))

        return data


class JobInterestSerializer(ModelSerializer):

    class Meta:
        model = JobInterest
        fields = '__all__'
