import itertools
import logging
import os
import uuid

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.mail import send_mail
from django.contrib.gis.geoip import GeoIP
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext_lazy as _

from allauth.account.signals import user_logged_in
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from .validators import UsernameValidator
from core.models import AbstractTimeStampedModel, optional
from core.utils import get_upload_path


logger = logging.getLogger('console_log')


class UserManager(BaseUserManager):
    """
    Model for a Custom user Manager
    """

    def _create_user(self, email, first_name, last_name, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        return self._create_user(email, first_name, last_name, password, False, False, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        return self._create_user(email, first_name, last_name, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    ACCOUNT_CANDIDATE = 1
    ACCOUNT_AGENT = 2
    ACCOUNT_SUPPORT = 3
    ACCOUNT_TYPE_CHOICES = (
        (ACCOUNT_CANDIDATE, _('Candidate')),
        (ACCOUNT_AGENT, _('Agent')),
        (ACCOUNT_SUPPORT, _('Support')),
    )

    STATUS_OFFLINE = 0
    STATUS_AWAY = 1
    STATUS_ONLINE = 2

    username_validator = UsernameValidator()

    email = models.EmailField(_('Email Address'), max_length=254, unique=True)
    username = models.CharField(
        _('Username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and ./_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        }
    )
    first_name = models.CharField(_('First Name'), max_length=30)
    last_name = models.CharField(_('Last Name'), max_length=30)
    slug = models.SlugField(_('Alias/Slug'), unique=True, **optional)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=('Designates whether this user should be treated as '
                   'active. Unselect this instead of deleting accounts.')
    )
    get_ads = models.BooleanField(_('Receive ads by email?'), default=True)
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)
    account_type = models.IntegerField(
        _('Account Type'),
        choices=ACCOUNT_TYPE_CHOICES,
        default=ACCOUNT_CANDIDATE,
        help_text='User role selected during registration'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    index_together = [
        ['slug', 'is_active'],
    ]

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_absolute_url(self):
        return "/user/{}/".format(self.slug)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return '{} {}'.format(self.first_name, self.last_name).strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return '{} {}'.format(self.first_name, self.last_name[0].upper())

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def last_seen(self):
        return cache.get(f'seen_{self.email}')

    def online(self):
        last_seen = self.last_seen()
        idle = cache.get(f'idle_{self.email}')
        if idle:
            return self.STATUS_AWAY
        if last_seen:
            now = timezone.now()
            if now > last_seen + timezone.timedelta(
                    seconds=settings.USER_ONLINE_TIMEOUT):
                return self.STATUS_OFFLINE
            else:
                return self.STATUS_ONLINE
        else:
            return self.STATUS_OFFLINE

    def get_photo_url(self):
        try:
            return self.profile.photo.url
        except ValueError:
            return static('img/default_user.jpg')

    @property
    def domain(self):
        """
        Retrieves the domain name from the email address.
        """
        return self.email[self.email.find('@') + 1:]

    @property
    def profile(self):
        if self.account_type == self.ACCOUNT_CANDIDATE:
            return self.candidate
        elif self.account_type == self.ACCOUNT_AGENT:
            return self.agent
        elif self.account_type == self.ACCOUNT_SUPPORT:
            return self.support

    def save(self, *args, **kwargs):
        if not self.pk:
            # slug
            self.slug = slug_copy = slugify(self.get_full_name())
            for i in itertools.count(1):
                if not User.objects.filter(slug=self.slug).exists():
                    break
                self.slug = '{}-{}'.format(slug_copy, i)

            # username
            self.username = username_copy = '{}{}'.format(self.first_name, self.last_name).replace(' ', '')
            for i in itertools.count(1):
                if not User.objects.filter(username=self.username).exists():
                    break
                self.username = '{}{}'.format(username_copy, i)

        return super(User, self).save(*args, **kwargs)


class ProfileBase(AbstractTimeStampedModel):
    """
    Abstract model for Profile.
    """
    # Status choices
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    STATUS_MODERATION = 2

    STATUS_CHOICES = (
        (STATUS_ACTIVE, _('Active')),
        (STATUS_INACTIVE, _('Inactive')),
        (STATUS_MODERATION, _('Moderation'))
    )

    phone = PhoneNumberField(_('Phone'), **optional)
    photo = models.ImageField(_('Photo'), upload_to=get_upload_path, help_text="200x200px", **optional)
    status = models.IntegerField(_('Status'), choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        abstract = True

    index_together = [
        ["user", "status"],
    ]

    def __str__(self):
        return '%s' % (self.user)


class Candidate(ProfileBase):
    """
    Model for Candidate.
    """
    JOB_TYPE_CONTRACT = 0
    JOB_TYPE_PERMANENT = 1

    JOB_TYPE_CHOICES = (
        (JOB_TYPE_CONTRACT, _('Contract')),
        (JOB_TYPE_PERMANENT, _('Permanent')),
    )

    STATUS_LOOKING_FOR_CONTRACT = 1
    STATUS_IN_CONTRACT = 2
    STATUS_OUT_OF_CONTRACT = 3

    STATUS_CHOICES = (
        (STATUS_LOOKING_FOR_CONTRACT, _('Currently Looking for a new contract')),
        (STATUS_IN_CONTRACT, _('Currently in Contract')),
        (STATUS_OUT_OF_CONTRACT, _('Currently out of contract')),
    )

    IN_CONTRACT_STATUS_OPEN = 1
    IN_CONTRACT_STATUS_LOOKING = 2

    IN_CONTRACT_STATUS_CHOICES = (
        (IN_CONTRACT_STATUS_OPEN, _('Open to new opportunities')),
        (IN_CONTRACT_STATUS_LOOKING, _('Actively looking for new opportunities')),
    )

    OUT_CONTRACT_STATUS_LOOKING = 1
    OUT_CONTRACT_STATUS_NOT_LOOKING = 2

    OUT_CONTRACT_STATUS_CHOICES = (
        (OUT_CONTRACT_STATUS_LOOKING, _('Currently looking for new opportunities')),
        (OUT_CONTRACT_STATUS_NOT_LOOKING, _('Not looking for new opportunities')),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate')
    title = models.CharField(_('Job title'), max_length=200)
    skills = models.ManyToManyField(
        'recruit.Skill',
        related_name='candidates',
        through='users.CandidateSkill',
        verbose_name=_('Skills')
    )
    job_type = models.IntegerField(_('Job type'), choices=JOB_TYPE_CHOICES, **optional)
    experience = models.SmallIntegerField(_('Experience (full years)'), **optional)
    city = models.CharField(_('City'),  max_length=200)
    country = CountryField(_('Country'))
    desired_city = models.CharField(_('Desired City'),  max_length=200, **optional)
    desired_country = CountryField(_('Desired Country'), **optional)
    willing_to_relocate = models.NullBooleanField(_('Willing to relocate?'), **optional)
    cv = models.FileField(_("CV"), upload_to=get_upload_path, max_length=150, editable=True, **optional)
    status = models.IntegerField(_('Status'), choices=STATUS_CHOICES, default=STATUS_LOOKING_FOR_CONTRACT)
    in_contract_status = models.IntegerField(_('In Contract Status'), choices=IN_CONTRACT_STATUS_CHOICES, **optional)
    out_contract_status = models.IntegerField(_('Out of Contract Status'), choices=OUT_CONTRACT_STATUS_CHOICES, **optional)

    class Meta:
        verbose_name = _('Candidate')
        verbose_name_plural = _('Candidates')

    def __str__(self):
        return self.user.get_full_name()

    def clean(self):
        validations = {}

        if self.status == self.STATUS_IN_CONTRACT and not self.in_contract_status:
            validations['in_contract_status'] = _('This field is required.')

        if self.status == self.STATUS_OUT_OF_CONTRACT and not self.out_contract_status:
            validations['out_contract_status'] = _('This field is required.')

        if validations:
            raise ValidationError(validations)

    @property
    def location(self):
        if self.city and self.country:
            return '{}, {}'.format(self.city, self.country.name)
        return None

    @property
    def desired_location(self):
        if self.desired_city and self.desired_country:
            return '{}, {}'.format(self.desired_city, self.desired_country.name)
        return None

    @property
    def willing_to_relocate_text(self):
        if self.willing_to_relocate == True:
            return 'Yes'
        elif self.willing_to_relocate == False:
            return 'No'
        else:
            return None

    @property
    def candidate_skills(self):
        return self.core_skills.filter(candidate=self)

    @property
    def cv_file_name(self):
        if self.cv:
            directory, file_name = os.path.split(self.cv.name)
            return file_name
        return None

    @property
    def is_initial_profile_complete(self):
        if self.photo and self.city and self.country and self.title:
            return True
        return False


class Agent(ProfileBase):
    """
    Model for Agent.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent')
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        verbose_name=_('Company'),
        related_name='agents',
        **optional
    )

    class Meta:
        verbose_name = _('Agent')
        verbose_name_plural = _('Agents')

    def __str__(self):
        return self.user.get_full_name()

    @property
    def is_initial_profile_complete(self):
        if self.photo:
            return True
        return False


class Support(ProfileBase):
    """
    Model for IT Support.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support')
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        verbose_name=_('Company'),
        related_name='supports',
        **optional
    )

    class Meta:
        verbose_name = _('Support')
        verbose_name_plural = _('Supports')

    def __str__(self):
        return self.user.get_full_name()

    @property
    def is_initial_profile_complete(self):
        if self.photo:
            return True
        return False


class UserNote(AbstractTimeStampedModel):
    """
    Model for User Note.
    """
    TYPE_TEXT = 1
    TYPE_CALL = 2
    TYPE_MAIL = 3

    TYPE_CHOICES = (
        (TYPE_TEXT, _('Text')),
        (TYPE_CALL, _('Call')),
        (TYPE_MAIL, _('Mail')),
    )
    note_by = models.ForeignKey('users.User', related_name='notes_written', verbose_name=_('Note by'))
    note_to = models.ForeignKey('users.User', related_name='notes_given', verbose_name=_('Note To'))
    text = models.TextField(_('Text'))
    type = models.IntegerField(_('Type'), choices=TYPE_CHOICES)

    class Meta:
        verbose_name = _('User Note')
        verbose_name_plural = _('User Notes')

    def __str__(self):
        return self.note_to.get_full_name()


class CandidateSkill(AbstractTimeStampedModel):
    """
    Model for Candidate Skill.
    """
    candidate = models.ForeignKey('users.Candidate', related_name='core_skills', verbose_name=_('Candidate'))
    skill = models.ForeignKey('recruit.Skill', related_name='candidate_skills', verbose_name=_('Skill'))
    experience = models.SmallIntegerField(_('Years of Experience'))

    class Meta:
        verbose_name = _('Candidate Skill')
        verbose_name_plural = _('Candidate Skills')

    def __str__(self):
        return self.skill.name


class CandidateSettings(AbstractTimeStampedModel):
    """
    Model for Candidate Settings.
    """
    candidate = models.OneToOneField('users.Candidate', related_name='settings', verbose_name=_('Candidate'))
    auto_cv_download = models.BooleanField(_('Automatic Download of CV?'), default=False)

    class Meta:
        verbose_name = _('Candidate Settings')
        verbose_name_plural = _('Candidate Settings')

    def __str__(self):
        return self.candidate.user.get_full_name()


class CVRequest(AbstractTimeStampedModel):
    """
    Model for CV Request.
    """

    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    STATUS_DECLINED = 2
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_DECLINED, 'Declined'),
    )

    candidate = models.ForeignKey('users.Candidate', related_name='cv_requests', verbose_name=_('Candidate'))
    requested_by = models.ForeignKey('users.User', related_name='cv_requests', verbose_name=_('User'))
    uuid = models.UUIDField(_('Automatic Download of CV?'), default=uuid.uuid4, editable=False)
    status = models.IntegerField(_('Status'), choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        verbose_name = _('CV Request')
        verbose_name_plural = _('CV Requests')

    def __str__(self):
        return self.candidate.user.get_full_name()


class UserLocation(AbstractTimeStampedModel):
    """
    Model for location tracking.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='location',
        **optional
    )
    ip_address = models.CharField(_('IP Address'), max_length=50, **optional)
    country_code = models.CharField(_('Country Code'), max_length=100, **optional)
    country_name = models.CharField(_('Country Name'), max_length=100, **optional)
    city = models.CharField(_('City'), max_length=100, **optional)
    latitude = models.FloatField(_('Latitude'), **optional)
    longitude = models.FloatField(_('Longitude'), **optional)
    continent_code = models.CharField(_('Continent Code'), max_length=20, **optional)

    class Meta:
        verbose_name = _('User location')
        verbose_name_plural = _('User locations')

    @property
    def get_on_google_maps(self):
        return 'https://www.google.com/maps/place/{}+{}/@{},{},13z'.format(
            self.latitude,
            self.longitude,
            self.latitude,
            self.longitude
        )
