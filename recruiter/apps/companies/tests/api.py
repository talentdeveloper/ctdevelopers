import json

from django.contrib.auth import (
    hashers,
    get_user_model,
)
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from core.tests import BaseTest
from companies.models import (
    CompanyRequestInvitation,
)
from users.models import Agent


User = get_user_model()


class CompanyInvitationAPITests(BaseTest):

    def setUp(self):
        super(CompanyInvitationAPITests, self).setUp()

    def test_accept_company_invitation_request(self):
        self.client.login(username=self.user_agent.email, password='agent')

        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent2.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        agent = G(
            Agent,
            user=user,
            company=None
        )

        company_request_invitation = G(
            CompanyRequestInvitation,
            user=user,
            company=self.company
        )

        response = self.client.post(
            reverse('companies:company_invitation_request', kwargs={'uuid': company_request_invitation.uuid}),
            {
                'action': 'accept',
            }
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        agent.refresh_from_db()
        company_request_invitation = CompanyRequestInvitation.objects.filter(user=user, company=self.company)

        self.assertTrue(payload.get('success'))
        self.assertFalse(company_request_invitation.exists())
        self.assertEqual(agent.company, self.company)

    def test_decline_company_invitation_request(self):
        self.client.login(username=self.user_agent.email, password='agent')

        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent2.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        agent = G(
            Agent,
            user=user,
            company=None
        )

        company_request_invitation = G(
            CompanyRequestInvitation,
            user=user,
            company=self.company
        )

        response = self.client.post(
            reverse('companies:company_invitation_request', kwargs={'uuid': company_request_invitation.uuid}),
            {
                'action': 'decline',
            }
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        company_request_invitation = CompanyRequestInvitation.objects.filter(user=user, company=self.company)

        self.assertTrue(payload.get('success'))
        self.assertFalse(company_request_invitation.exists())
        self.assertNotEqual(agent.company, self.company)
