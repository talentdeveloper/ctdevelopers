from django.contrib.auth import (
    get_user_model,
    hashers,
)
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from chat.models import (
    Conversation,
    Message,
    Participant,
)
from core.tests import BaseTest
from companies.models import (
    Company,
    CompanyInvitation,
)
from recruit.models import (
    Connection,
    ConnectionInvite,
    ConnectionRequest,
    Skill,
)
from users.models import (
    Agent,
    Candidate,
    UserNote,
    CVRequest,
)


User = get_user_model()


class SignupViewTests(BaseTest):

    def setUp(self):
        super(SignupViewTests, self).setUp()

    def test_signup_candidate(self):
        response = self.client.post(
            reverse('account_signup'),
            {
                'email': 'test@candidate.com',
                'first_name': 'candidate',
                'last_name': 'candidate',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_CANDIDATE,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        user = User.objects.get(email='test@candidate.com')

        self.assertTrue(user)
        self.assertTrue(user.candidate)

    def test_signup_agent(self):
        response = self.client.post(
            reverse('account_signup'),
            {
                'email': 'test@agent.com',
                'first_name': 'agent',
                'last_name': 'agent',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_AGENT,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email='test@agent.com')

        self.assertTrue(user)
        self.assertTrue(user.agent)

    def test_signup_connection_invite(self):
        connection_invite = G(
            ConnectionInvite,
            connecter=self.user_candidate,
            connectee_email='test@candidate.com',
        )

        response = self.client.post(
            '{}?invite_type={}&account_type={}&uuid={}&email={}'.format(
                reverse('account_signup'),
                'connection',
                User.ACCOUNT_CANDIDATE,
                connection_invite.uuid,
                connection_invite.connectee_email
            ),
            {
                'email': 'test@candidate.com',
                'first_name': 'candidate',
                'last_name': 'candidate',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_CANDIDATE,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        user = User.objects.get(email='test@candidate.com')

        self.assertTrue(user)
        self.assertTrue(user.candidate)

        connection = Connection.objects.filter(
            connecter=connection_invite.connecter,
            connectee=user
        )

        self.assertTrue(connection.exists())

    def test_signup_company_invite(self):
        company_invite = G(
            CompanyInvitation,
            inviter=self.user_agent,
            invitee_email='test@agent.com',
        )

        response = self.client.post(
            '{}?invite_type={}&account_type={}&uuid={}&email={}&company_type={}'.format(
                reverse('account_signup'),
                'company',
                User.ACCOUNT_AGENT,
                company_invite.uuid,
                company_invite.invitee_email,
                Company.COMPANY_RECRUITMENT
            ),
            {
                'email': 'test@agent.com',
                'first_name': 'agent',
                'last_name': 'agent',
                'phone': '+639771234567',
                'account_type': User.ACCOUNT_AGENT,
                'password1': 'password',
                'password2': 'password',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:dashboard'))

        user = User.objects.get(email='test@agent.com')

        self.assertTrue(user)
        self.assertTrue(user.agent)
        self.assertEqual(user.agent.company, company_invite.inviter.agent.company)


class ProfileViewTests(BaseTest):

    def setUp(self):
        super(ProfileViewTests, self).setUp()

        self.skill = G(Skill)

        G(
            CVRequest,
            candidate=self.candidate,
            requested_by=self.user_agent
        )

        self.user_note = G(
            UserNote,
            note_by=self.user_agent,
            note_to=self.user_candidate
        )

        G(
            Connection,
            connecter=self.user_candidate,
            connectee=self.user_agent
        )

    def test_candidate_profile_own(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.get(reverse('users:candidate_profile', kwargs={'slug': self.user_candidate.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('is_connected'))
        self.assertEqual(response.context.get('skills'), [self.skill.name])
        self.assertEqual(response.context.get('ConnectionRequest'), ConnectionRequest)

    def test_candidate_profile_other(self):
        self.client.login(username=self.user_agent.email, password='agent')

        conversation = G(
            Conversation,
            conversation_type=Conversation.CONVERSATION_USER
        )

        Participant.objects.create(
            status=Participant.PARTICIPANT_ACCEPTED,
            user=self.user_agent,
            conversation=conversation
        )
        Participant.objects.create(
            status=Participant.PARTICIPANT_ACCEPTED,
            user=self.user_candidate,
            conversation=conversation
        )

        message_agent = G(
            Message,
            author=self.user_agent,
            conversation=conversation
        )
        message_candidate = G(
            Message,
            author=self.user_candidate,
            conversation=conversation
        )

        response = self.client.get(reverse('users:candidate_profile', kwargs={'slug': self.user_candidate.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('cv_request'))
        self.assertEqual(response.context.get('user_note'), UserNote)
        self.assertIn(self.user_note, response.context.get('user_notes'))
        self.assertTrue(response.context.get('is_connected'))
        self.assertEqual(response.context.get('first_contact_sent'), message_agent)
        self.assertEqual(response.context.get('last_message_sent'), message_agent)
        self.assertEqual(response.context.get('last_message_received'), message_candidate)

    def test_candidate_profile_update(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:profile_update'),
            {
                'phone': '+639771234567',
                'title': 'title',
                'job_type': Candidate.JOB_TYPE_CONTRACT,
                'experience': 10,
                'city': 'city',
                'country': 'PH',
                'desired_city': 'desired city',
                'desired_country': 'PH',
                'willing_to_relocate': True,
                'status': Candidate.STATUS_LOOKING_FOR_CONTRACT,
                'in_contract_status': Candidate.IN_CONTRACT_STATUS_OPEN,
                'out_contract_status': Candidate.OUT_CONTRACT_STATUS_LOOKING,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile_update'))

    def test_agent_profile_update(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(reverse('users:profile_update'), {
            'phone': '+639771234567',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile_update'))


class SearchViewTest(BaseTest):

    def setUp(self):
        super(SearchViewTest, self).setUp()

    def test_candidate_search(self):
        self.client.login(username=self.user_candidate.email, password='candidate')
        user = G(
            User,
            email='candidate2@candidate.com',
            first_name='candidate2',
            last_name='candidate2',
            password=hashers.make_password('candidate2'),
            account_type=User.ACCOUNT_CANDIDATE
        )
        candidate = G(
            Candidate,
            user=user
        )

        response = self.client.get(
            reverse('users:candidate_search'),
            {'search': 'candidate2'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('search'), 'candidate2')
        self.assertIn(candidate, response.context.get('candidates'))
        self.assertEqual(response.context.get('connection_request'), ConnectionRequest)

    def test_agent_search(self):
        self.client.login(username=self.user_agent.email, password='agent')
        user = G(
            User,
            email='agent2@agent.com',
            first_name='agent2',
            last_name='agent2',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        agent = G(
            Agent,
            user=user
        )

        response = self.client.get(
            reverse('users:agent_search'),
            {'search': 'agent2'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('search'), 'agent2')
        self.assertIn(agent, response.context.get('agents'))
        self.assertEqual(response.context.get('connection_request'), ConnectionRequest)


class SettingsViewTests(BaseTest):

    def setUp(self):
        super(SettingsViewTests, self).setUp()

    def test_candidate_settings_page(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.get(reverse('users:settings'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_agent_settings_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(reverse('users:settings'))

        self.assertEqual(response.status_code, 200)

    def test_candidate_settings_update(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:settings_update'),
            {
                'auto_cv_download': True,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:settings'))


class CVRequestViewTests(BaseTest):

    def setUp(self):
        super(CVRequestViewTests, self).setUp()

    def test_cv_request(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('users:cv_request', kwargs={'slug': self.user_candidate.slug}),
            {
                'status': CVRequest.STATUS_PENDING,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:candidate_profile', kwargs={'slug': self.user_candidate.slug}))

        cv_request = CVRequest.objects.filter(candidate=self.candidate, requested_by=self.user_agent)

        self.assertTrue(cv_request.exists())
