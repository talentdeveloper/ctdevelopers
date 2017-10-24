from django.contrib.auth import get_user_model

from django_dynamic_fixture import G

from core.tests import BaseTest
from recruit.forms import (
    JobPostForm,
)
from recruit.models import (
    JobPost,
    Skill,
)


User = get_user_model()


class JobPostFormTests(BaseTest):

    def setUp(self):
        super(JobPostFormTests, self).setUp()

        self.skill = G(Skill)

        self.job_post = G(
            JobPost,
            posted_by=self.agent
        )

    def test_valid_create_job_post_form(self):
        form = JobPostForm(
            initial={
                'agent': self.agent,
            },
            data={
                'title': 'test',
                'description': 'test',
                'contract': 'test',
                'city': 'test',
                'country': 'PH',
                'skills': [self.skill],
            }
        )

        self.assertTrue(form.is_valid())

        job_post = form.save()

        self.assertTrue(job_post)

    def test_invalid_create_job_post_form(self):
        form = JobPostForm(
            initial={
                'agent': self.agent,
            },
            data={}
        )

        self.assertFalse(form.is_valid())

    def test_valid_update_job_post_form(self):
        form = JobPostForm(
            instance=self.job_post,
            data={
                'title': 'test',
                'description': 'test',
                'contract': 'test',
                'city': 'test',
                'country': 'PH',
                'skills': [self.skill],
            }
        )

        self.assertTrue(form.is_valid())

        job_post = form.save()

        self.assertTrue(job_post)

    def test_invalid_update_job_post_form(self):
        form = JobPostForm(
            instance=self.job_post,
            data={}
        )

        self.assertFalse(form.is_valid())
