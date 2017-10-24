from tempfile import NamedTemporaryFile

from django.contrib.auth import (
    get_user_model,
    hashers,
)
from django.core.files import File
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G
from PIL import Image

from chat.models import (
    Conversation,
    Message,
    Participant,
)
from core.tests import BaseTest
from companies.models import (
    Company,
    CompanyInvitation,
    CompanyRequestInvitation,
)
from recruit.models import (
    Connection,
    ConnectionRequest,
)
from users.models import (
    Agent,
    UserNote,
)


User = get_user_model()


class CompanyViewTests(BaseTest):

    def setUp(self):
        super(CompanyViewTests, self).setUp()

        image = Image.new('RGB', size=(10, 10))
        file = NamedTemporaryFile(suffix='.jpg')
        image.save(file)
        self.image = File(open(file.name, 'rb'))

    def test_valid_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_update'),
            {
                'name': 'agent',
                'domain': 'agent.com',
                'overview': 'agent',
                'description': 'agent',
                'logo': self.image,
                'address_1': 'agent',
                'address_2': 'agent',
                'zip': 'agent',
                'city': 'agent',
                'country': 'PH',
                'website': 'http://www.agent.com',
                'is_charity': True,
                'allow_auto_invite': True,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('company'), self.company)

    def test_invald_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_update'),
            {}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('form').errors)

    def test_valid_create_company(self):
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
        self.client.login(username=user.email, password='agent2')

        response = self.client.post(
            reverse('companies:company_create'),
            {
                'name': 'agent2',
                'domain': 'agent2.com',
                'city': 'agent2',
                'country': 'PH',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        agent.refresh_from_db()
        company = Company.objects.filter(domain='agent2.com')

        self.assertTrue(company.exists())
        self.assertEqual(agent.company, company.first())

    def test_invalid_create_company(self):
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
        self.client.login(username=user.email, password='agent2')

        response = self.client.post(
            reverse('companies:company_create'),
            {}
        )

        self.assertEqual(response.status_code, 200)

        company = Company.objects.filter(agents=agent)

        self.assertFalse(company.exists())

    def test_create_company_agent_with_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_create'),
            {
                'name': 'agent2',
                'domain': 'agent2.com',
                'city': 'agent2',
                'country': 'PH',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        company = Company.objects.filter(domain='agent2.com')

        self.assertFalse(company.exists())

    def test_company_pending_page(self):
        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent2.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        G(
            Agent,
            user=user,
            company=None
        )
        self.client.login(username=user.email, password='agent2')

        response = self.client.get(reverse('companies:company_pending'))

        self.assertEqual(response.status_code, 200)

    def test_company_pending_with_company_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(reverse('companies:company_pending'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

    def test_company_detail_page_company_owner(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent2.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        G(
            Agent,
            user=user,
            company=None
        )

        company_request_invitation = G(
            CompanyRequestInvitation,
            company=self.company,
            user=user
        )

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.company.owner
        )

        connection = G(
            Connection,
            connectee=self.user_candidate,
            connecter=self.company.owner
        )

        connection_request = G(
            ConnectionRequest,
            connectee=self.user_candidate,
            connecter=self.company.owner
        )

        conversation = G(
            Conversation,
            conversation_type=Conversation.CONVERSATION_USER
        )

        Participant.objects.create(
            status=Participant.PARTICIPANT_ACCEPTED,
            user=self.company.owner,
            conversation=conversation
        )
        Participant.objects.create(
            status=Participant.PARTICIPANT_ACCEPTED,
            user=self.user_candidate,
            conversation=conversation
        )

        message_agent = G(
            Message,
            author=self.company.owner,
            conversation=conversation
        )
        message_candidate = G(
            Message,
            author=self.user_candidate,
            conversation=conversation
        )

        response = self.client.get(reverse('companies:company_detail', kwargs={'slug': self.company.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('company'), self.company)
        self.assertIn(company_request_invitation, response.context.get('invitation_requests'))
        self.assertEqual(response.context.get('current_profile'), self.company.owner.agent)

        self.assertEqual(response.context.get('user_note'), UserNote)
        self.assertIn(user_note, response.context.get('user_notes'))

        self.assertEqual(response.context.get('current_profile_connection'), connection)
        self.assertEqual(response.context.get('connection_request'), ConnectionRequest)
        self.assertEqual(response.context.get('current_profile_connection_request'), connection_request)

        self.assertEqual(response.context.get('first_contact_sent'), message_candidate)
        self.assertEqual(response.context.get('last_message_sent'), message_candidate)
        self.assertEqual(response.context.get('last_message_received'), message_agent)
        self.assertEqual(response.context.get('last_person_in_contact').user, self.company.owner)
        self.assertEqual(response.context.get('last_person_added_manual_track'), self.company.owner)

    def test_company_detail_page_company_staff(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        new_agent_user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent2.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        new_agent = G(
            Agent,
            user=new_agent_user,
            company=self.company
        )

        company_request_invitation = G(
            CompanyRequestInvitation,
            company=self.company,
            user=new_agent_user
        )

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=new_agent_user
        )

        connection = G(
            Connection,
            connectee=self.user_candidate,
            connecter=new_agent_user
        )

        connection_request = G(
            ConnectionRequest,
            connectee=self.user_candidate,
            connecter=new_agent_user
        )

        conversation = G(
            Conversation,
            conversation_type=Conversation.CONVERSATION_USER
        )

        Participant.objects.create(
            status=Participant.PARTICIPANT_ACCEPTED,
            user=new_agent_user,
            conversation=conversation
        )
        Participant.objects.create(
            status=Participant.PARTICIPANT_ACCEPTED,
            user=self.user_candidate,
            conversation=conversation
        )

        message_agent = G(
            Message,
            author=new_agent_user,
            conversation=conversation
        )
        message_candidate = G(
            Message,
            author=self.user_candidate,
            conversation=conversation
        )

        response = self.client.get(
            reverse('companies:company_detail', kwargs={'slug': self.company.slug}),
            {'profile': new_agent.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('company'), self.company)
        self.assertIn(company_request_invitation, response.context.get('invitation_requests'))
        self.assertEqual(response.context.get('current_profile'), new_agent)

        self.assertEqual(response.context.get('user_note'), UserNote)
        self.assertIn(user_note, response.context.get('user_notes'))

        self.assertEqual(response.context.get('current_profile_connection'), connection)
        self.assertEqual(response.context.get('connection_request'), ConnectionRequest)
        self.assertEqual(response.context.get('current_profile_connection_request'), connection_request)

        self.assertEqual(response.context.get('first_contact_sent'), message_candidate)
        self.assertEqual(response.context.get('last_message_sent'), message_candidate)
        self.assertEqual(response.context.get('last_message_received'), message_agent)
        self.assertEqual(response.context.get('last_person_in_contact').user, new_agent_user)
        self.assertEqual(response.context.get('last_person_added_manual_track'), new_agent_user)


class CompanyInviteViewTests(BaseTest):

    def setUp(self):
        super(CompanyInviteViewTests, self).setUp()

    def test_invalid_update_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_update'),
            {}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('form').errors)

    def test_valid_invite_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_invite'),
            {
                'invitee_email': 'agent2@agent.com',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_detail', kwargs={'slug': self.company.slug}))

        company_invitation = CompanyInvitation.objects.filter(invitee_email='agent2@agent.com')

        self.assertTrue(company_invitation.exists())

    def test_invalid_invite_company(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('companies:company_invite'),
            {}
        )

        self.assertEqual(response.status_code, 200)

        company_invitation = CompanyInvitation.objects.all()

        self.assertFalse(company_invitation.exists())

    def test_company_invite_success_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(reverse('companies:company_invite_success'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('company'), self.company)
