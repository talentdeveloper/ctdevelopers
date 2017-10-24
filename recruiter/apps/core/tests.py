from django.contrib.auth import (
    get_user_model,
    hashers,
)
from django.test import TestCase
from django.test.client import Client

from django_dynamic_fixture import G

from companies.models import Company
from users.models import (
    Agent,
    Candidate,
    CandidateSettings,
)


User = get_user_model()


class BaseTest(TestCase):

    def setUp(self):
        self.user_candidate = G(
            User,
            email='candidate@candidate.com',
            first_name='candidate',
            last_name='candidate',
            password=hashers.make_password('candidate'),
            account_type=User.ACCOUNT_CANDIDATE
        )
        self.candidate = G(
            Candidate,
            user=self.user_candidate
        )
        self.candidate_settings = G(
            CandidateSettings,
            candidate=self.candidate
        )

        self.company = G(
            Company,
            name='agent',
            domain='agent.com'
        )
        self.user_agent = G(
            User,
            first_name='agent',
            last_name='agent',
            email='agent@agent.com',
            password=hashers.make_password('agent'),
            account_type=User.ACCOUNT_AGENT
        )
        self.agent = G(
            Agent,
            user=self.user_agent,
            company=self.company
        )
        self.company.owner = self.user_agent
        self.company.save()

        self.client = Client()
