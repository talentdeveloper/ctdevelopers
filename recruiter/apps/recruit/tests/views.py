from django.contrib.auth import (
    get_user_model,
    hashers,
)
from django.core.urlresolvers import reverse

from django_dynamic_fixture import G

from companies.models import CompanyRequestInvitation
from core.tests import BaseTest
from recruit.models import (
    Connection,
    ConnectionRequest,
    JobPost,
    JobReferral,
    Skill,
    UserReferral,
)
from users.models import (
    Agent,
    CVRequest,
)


User = get_user_model()


class IndexViewTests(BaseTest):

    def setUp(self):
        super(IndexViewTests, self).setUp()

    def test_home_page(self):
        response = self.client.get(reverse('recruit:home'))

        self.assertEqual(response.status_code, 200)

    def test_candidate_dashboard_page(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        connection_request = G(
            ConnectionRequest,
            connectee=self.user_candidate,
            connecter=self.user_agent,
        )

        connection = G(
            Connection,
            connectee=self.user_candidate,
            connecter=self.user_agent,
        )

        job_referral = G(
            JobReferral,
            referred_to=self.candidate
        )

        candidate_referral = G(
            UserReferral,
            referred_to=self.user_candidate,
            referred_user=self.user_candidate
        )
        agent_referral = G(
            UserReferral,
            referred_to=self.user_candidate,
            referred_user=self.user_agent
        )

        cv_request = G(
            CVRequest,
            candidate=self.candidate,
            status=CVRequest.STATUS_PENDING
        )

        response = self.client.get(reverse('recruit:dashboard'))
        self.assertEqual(response.status_code, 200)

        self.assertIn(connection_request, response.context.get('connection_requests'))
        self.assertIn(connection, response.context.get('connections'))

        self.assertIn(job_referral, response.context.get('job_referrals'))

        self.assertIn(candidate_referral, response.context.get('candidate_referrals'))
        self.assertIn(agent_referral, response.context.get('agent_referrals'))

        self.assertIn(cv_request, response.context.get('cv_requests'))

    def test_agent_dashboard_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        connection_request = G(
            ConnectionRequest,
            connecter=self.user_candidate,
            connectee=self.user_agent,
        )

        connection = G(
            Connection,
            connecter=self.user_candidate,
            connectee=self.user_agent,
        )

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 200)

        self.assertIn(connection_request, response.context.get('connection_requests'))
        self.assertIn(connection, response.context.get('connections'))

    def test_agent_dashboard_page_without_company(self):
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

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_create'))

    def test_agent_dashboard_page_without_company_with_existing_domain_auto_invite_activated(self):
        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        agent = G(
            Agent,
            user=user,
            company=None
        )

        self.client.login(username=user.email, password='agent2')

        self.company.allow_auto_invite = True
        self.company.save()

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_invite_success'))

        agent.refresh_from_db()

        self.assertEqual(agent.company, self.company)

    def test_agent_dashboard_page_without_company_with_existing_domain_auto_invite_deactivated(self):
        user = G(
            User,
            first_name='agent2',
            last_name='agent2',
            email='agent2@agent.com',
            password=hashers.make_password('agent2'),
            account_type=User.ACCOUNT_AGENT
        )
        agent = G(
            Agent,
            user=user,
            company=None
        )

        self.client.login(username=user.email, password='agent2')

        self.company.allow_auto_invite = False
        self.company.save()

        response = self.client.get(reverse('recruit:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('companies:company_pending'))

        agent.refresh_from_db()
        company_request_invitation = CompanyRequestInvitation.objects.filter(user=user, company=self.company)

        self.assertIsNone(agent.company)
        self.assertTrue(company_request_invitation.exists())


class SearchViewTests(BaseTest):

    def setUp(self):
        super(SearchViewTests, self).setUp()

        self.skill = G(Skill)

    def test_search_candidate(self):
        self.candidate.city = 'Davao'
        self.candidate.country = 'PH'
        self.candidate.save()

        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(
            reverse('recruit:search'),
            {
                'search': 'candidate',
                'filters': 'Davao,PH',
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn('Philippines', response.context.get('countries'))
        self.assertIn('Davao', response.context.get('cities'))

        self.assertEqual(response.context.get('connection_request'), ConnectionRequest)
        self.assertIn(self.skill, response.context.get('skills'))

        self.assertIn(self.candidate, response.context.get('results'))
        self.assertIn('Davao', response.context.get('filters'))
        self.assertIn('PH', response.context.get('filters'))
        self.assertIn('candidate', response.context.get('search'))

    def test_search_job_post(self):
        job_post = G(
            JobPost,
            posted_by=self.agent,
            title='test',
            city='Davao',
            country='PH'
        )

        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.get(
            reverse('recruit:search'),
            {
                'search': 'test',
                'filters': 'Davao,PH',
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn('Philippines', response.context.get('countries'))
        self.assertIn('Davao', response.context.get('cities'))

        self.assertEqual(response.context.get('connection_request'), ConnectionRequest)
        self.assertIn(self.skill, response.context.get('skills'))

        self.assertIn(job_post, response.context.get('results'))
        self.assertIn('Davao', response.context.get('filters'))
        self.assertIn('PH', response.context.get('filters'))
        self.assertIn('test', response.context.get('search'))


class JobPostViewTests(BaseTest):

    def setUp(self):
        super(JobPostViewTests, self).setUp()

        self.skill = G(Skill)

        self.job_post = G(
            JobPost,
            posted_by=self.agent
        )

    def test_job_post_list_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(reverse('recruit:job_post_list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.job_post, response.context.get('job_posts'))

    def test_job_post_detail_page(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.get(reverse('recruit:job_post_detail', kwargs={'uuid': self.job_post.uuid}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.job_post, response.context.get('job_post'))

    def test_valid_job_post_create(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('recruit:job_post_create'),
            {
                'title': 'test',
                'description': 'test',
                'contract': 'test',
                'city': 'test',
                'country': 'PH',
                'skills': [self.skill],
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:job_post_list'))

        job_post = JobPost.objects.filter(title='test')

        self.assertTrue(job_post.exists())
        self.assertEqual(job_post.first().posted_by, self.agent)

    def test_invalid_job_post_create(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('recruit:job_post_create'),
            {}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('form').errors)

    def test_valid_job_post_update(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('recruit:job_post_update', kwargs={'uuid': self.job_post.uuid}),
            {
                'title': 'test',
                'description': 'test',
                'contract': 'test',
                'city': 'test',
                'country': 'PH',
                'skills': [self.skill],
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:job_post_list'))

        job_post = JobPost.objects.filter(title='test')

        self.assertTrue(job_post.exists())
        self.assertEqual(job_post.first(), self.job_post)

    def test_invalid_job_post_update(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('recruit:job_post_update', kwargs={'uuid': self.job_post.uuid}),
            {}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context.get('form').errors)

    def test_invalid_job_post_delete(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('recruit:job_post_delete', kwargs={'uuid': self.job_post.uuid}),
            {}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recruit:job_post_list'))

        job_post = JobPost.objects.filter(uuid=self.job_post.uuid)

        self.assertFalse(job_post.exists())
