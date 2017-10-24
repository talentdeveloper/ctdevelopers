import shutil
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File

from PIL import Image

from core.tests import BaseTest
from companies.forms import (
    CompanyForm,
    CompanyUpdateForm,
    CompanyInvitationForm,
)
from companies.models import (
    CompanyInvitation,
)


User = get_user_model()


class CompanyFormTests(BaseTest):

    def setUp(self):
        super(CompanyFormTests, self).setUp()

        image = Image.new('RGB', size=(1, 1))
        file = NamedTemporaryFile(suffix='.jpg')
        new_file_name = settings.MEDIA_ROOT + '/comic.jpg'
        shutil.copy(file.name, new_file_name)
        image.save(new_file_name)
        self.image = File(open(new_file_name, 'rb'))

    def test_valid_update_company(self):
        form = CompanyUpdateForm(
            instance=self.company,
            data={
                'name': 'agent',
                'domain': 'agent@agent.com',
                'overview': 'agent',
                'description': 'agent',
                'address_1': 'agent',
                'address_2': 'agent',
                'zip': 'agent',
                'city': 'agent',
                'country': 'PH',
                'website': 'http://www.agent.com',
                'is_charity': True,
                'allow_auto_invite': True,
            },
            files={
                'logo': self.image,
            }
        )

        self.assertTrue(form.is_valid())

        company = form.save()

        self.assertTrue(company)

    def test_invalid_update_company(self):
        form = CompanyUpdateForm(
            instance=self.company,
            data={},
            files={}
        )

        self.assertFalse(form.is_valid())

    def test_valid_create_company(self):
        form = CompanyForm(
            initial={
                'user': self.user_agent,
            },
            data={
                'name': 'agent2',
                'domain': 'agent2.com',
                'city': 'agent2',
                'country': 'PH',
            }
        )

        self.assertTrue(form.is_valid())

        company = form.save()

        self.assertTrue(company)

    def test_invalid_create_company(self):
        form = CompanyForm(
            initial={
                'user': self.user_agent,
            },
            data={}
        )

        self.assertFalse(form.is_valid())


class CompanyInviteFormTests(BaseTest):

    def setUp(self):
        super(CompanyInviteFormTests, self).setUp()

    def test_valid_invite_company(self):
        form = CompanyInvitationForm(
            initial={
                'inviter': self.user_agent,
            },
            data={
                'invitee_email': 'agent2@agent.com',
            }
        )

        self.assertTrue(form.is_valid())

        company_invitation = form.save()
        company_invitation = CompanyInvitation.objects.filter(invitee_email='agent2@agent.com')

        self.assertEquals(company_invitation, company_invitation)

    def test_invalid_invite_company_invalid_domain(self):
        form = CompanyInvitationForm(
            initial={
                'inviter': self.user_agent,
            },
            data={
                'invitee_email': 'agent2@agent2.com',
            }
        )

        self.assertFalse(form.is_valid())

    def test_invalid_invite_company_duplicate_user_email(self):
        form = CompanyInvitationForm(
            initial={
                'inviter': self.user_agent,
            },
            data={
                'invitee_email': 'agent@agent.com',
            }
        )

        self.assertFalse(form.is_valid())
