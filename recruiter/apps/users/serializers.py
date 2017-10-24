from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from allauth.account.forms import ResetPasswordForm
from rest_auth.serializers import PasswordResetSerializer
from rest_framework import serializers

from .models import (
    Agent,
    Candidate,
    CandidateSettings,
    CandidateSkill,
    Support,
)
from companies.serializers import CompanySerializer
from core.serializers import ModelSerializer
from recruit.models import Skill


User = get_user_model()


class PasswordSerializer(PasswordResetSerializer):
    password_reset_form_class = ResetPasswordForm


class SkillSerializer(ModelSerializer):

    class Meta:
        model = Skill
        fields = '__all__'


class CandidateSkillSerializer(ModelSerializer):

    skill = SkillSerializer()

    class Meta:
        model = CandidateSkill
        fields = '__all__'


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'slug', 'date_joined', 'account_type',)


class CandidateSettingsSerializer(ModelSerializer):

    class Meta:
        model = CandidateSettings
        fields = '__all__'


class CandidateSerializer(ModelSerializer):

    user = UserSerializer()
    candidate_skills = CandidateSkillSerializer(many=True)
    settings = CandidateSettingsSerializer()
    country = serializers.SerializerMethodField()
    desired_country = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        exclude = ('skills',)

    def get_country(self, obj):
        return obj.country.name

    def get_desired_country(self, obj):
        return obj.desired_country.name

    def validate_candidate_skills(self, data):
        skills = [
            candidate_skill.get('skill').get('name')
            for candidate_skill in data
        ]
        experiences = [
            candidate_skill.get('experience')
            for candidate_skill in data
        ]

        if (not all(skill != None for skill in skills) or
            not all(experience != None for experience in experiences)):
            raise serializers.ValidationError(_('Please complete skill name and year of experience'))

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.save()

            # save user
            user = validated_data.get('user')
            if user != None:
                if user.get('email') != None:
                    instance.user.email = user.get('email')
                if user.get('username') != None:
                    instance.user.username = user.get('username')
                if user.get('first_name') != None:
                    instance.user.first_name = user.get('first_name')
                if user.get('last_name') != None:
                    instance.user.last_name = user.get('last_name')
            instance.user.save()

            # save candidate skills
            candidate_skills = validated_data.get('candidate_skills')
            if candidate_skills != None:
                CandidateSkill.objects.filter(candidate=instance).delete()
                for candidate_skill in candidate_skills:
                    skill = Skill.objects.filter(name__iexact=candidate_skill.get('name'))
                    if skill.exists():
                        skill = skill.first()
                    else:
                        skill = Skill.objects.create(name=candidate_skill.get('skill').get('name'))

                    CandidateSkill.objects.get_or_create(
                        defaults={
                            'skill': skill,
                        },
                        candidate=instance,
                        experience=candidate_skill.get('experience', 0)
                    )

            # save candidate settings
            settings = validated_data.get('settings')
            if settings != None:
                if settings.get('auto_cv_download') != None:
                    instance.settings.auto_cv_download = settings.get('auto_cv_download')
                instance.settings.save()

        return instance


class AgentSerializer(ModelSerializer):
    user = UserSerializer()
    company = CompanySerializer()

    class Meta:
        model = Agent
        fields = '__all__'

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.save()

            # save user
            user = validated_data.get('user')
            if user != None:
                if user.get('email') != None:
                    instance.user.email = user.get('email')
                if user.get('username') != None:
                    instance.user.username = user.get('username')
                if user.get('first_name') != None:
                    instance.user.first_name = user.get('first_name')
                if user.get('last_name') != None:
                    instance.user.last_name = user.get('last_name')
            instance.user.save()

        return instance


class SupportSerializer(ModelSerializer):
    user = UserSerializer()
    company = CompanySerializer()

    class Meta:
        model = Support
        fields = '__all__'

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.save()

            # save user
            user = validated_data.get('user')
            if user != None:
                if user.get('email') != None:
                    instance.user.email = user.get('email')
                if user.get('username') != None:
                    instance.user.username = user.get('username')
                if user.get('first_name') != None:
                    instance.user.first_name = user.get('first_name')
                if user.get('last_name') != None:
                    instance.user.last_name = user.get('last_name')
            instance.user.save()

        return instance
