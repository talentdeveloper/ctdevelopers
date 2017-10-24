from tempfile import NamedTemporaryFile

from django.contrib.auth import get_user_model
from django.core.files import File

from django_dynamic_fixture import G
from PIL import Image

from core.tests import BaseTest
from recruit.models import (
    Skill,
)
from users.forms import (
    AgentUpdateForm,
    AgentPhotoUploadForm,
    CandidateCVUploadForm,
    CandidatePhotoUploadForm,
    CandidateForm,
    CandidateUpdateForm,
    CandidateSettingsForm,
    CVRequestForm,
    UserNoteForm,
)
from users.models import (
    Candidate,
    CandidateSkill,
    CVRequest,
    UserNote,
)


User = get_user_model()


class ProfileFormTests(BaseTest):

    def setUp(self):
        super(ProfileFormTests, self).setUp()

        self.skill = G(Skill)

    def test_candidate_update_form(self):
        form = CandidateUpdateForm(data={
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
        })

        self.assertTrue(form.is_valid())

    def test_agent_update_form(self):
        form = AgentUpdateForm(data={
            'phone': '+639771234567',
        })

        self.assertTrue(form.is_valid())

    def test_valid_candidate_profile_update_form(self):
        form = CandidateForm(
            instance=self.candidate,
            data={
                'experience': 10,
                'city': 'city',
                'country': 'PH',
                'desired_city': 'city',
                'desired_country': 'PH',
                'willing_to_relocate': True,
                'status': Candidate.STATUS_LOOKING_FOR_CONTRACT,
                'in_contract_status': Candidate.IN_CONTRACT_STATUS_OPEN,
                'out_contract_status': Candidate.OUT_CONTRACT_STATUS_LOOKING,
                'form-TOTAL_FORMS': '1',
                'form-INITIAL_FORMS': '0',
                'form-MAX_NUM_FORMS': '',
                'form-0-skill': 'skill 1',
                'form-0-experience': 10,
            }
        )

        self.assertTrue(form.is_valid())

        form.save()

        skill = Skill.objects.filter(name='skill 1')
        candidate_skill = CandidateSkill.objects.filter(skill=skill, candidate=self.candidate)

        self.assertTrue(skill.exists())
        self.assertTrue(candidate_skill.exists())

    def test_invalid_candidate_profile_update_form(self):
        form = CandidateForm(data={})

        self.assertFalse(form.is_valid())


class SettingsFormTests(BaseTest):

    def setUp(self):
        super(SettingsFormTests, self).setUp()

    def test_candidate_settings_form(self):
        form = CandidateSettingsForm(data={
            'auto_cv_download': True,
        })

        self.assertTrue(form.is_valid())


class CVRequestFormTests(BaseTest):
    def setUp(self):
        super(CVRequestFormTests, self).setUp()

    def test_cv_request_form(self):
        form = CVRequestForm(
            data={
                'status': CVRequest.STATUS_PENDING,
            },
            initial={
                'candidate': self.candidate,
                'requested_by': self.user_agent,
            }
        )

        self.assertTrue(form.is_valid())

        cv_request = form.save()

        self.assertEqual(cv_request, CVRequest.objects.filter(candidate=self.candidate, requested_by=self.user_agent).first())


class FileUploadFormTests(BaseTest):

    def setUp(self):
        super(FileUploadFormTests, self).setUp()

        image = Image.new('RGB', size=(10, 10))
        file = NamedTemporaryFile(suffix='.jpg')
        image.save(file)
        self.image = File(open(file.name, 'rb'))

    def test_candidate_photo_upload_form(self):
        form = CandidatePhotoUploadForm(
            data={
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            },
            files={
                'photo': self.image,
            }
        )

        self.assertTrue(form.is_valid())

    def test_agent_photo_upload_form(self):
        form = AgentPhotoUploadForm(
            data={
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            },
            files={
                'photo': self.image,
            }
        )

        self.assertTrue(form.is_valid())

    def test_candidate_cv_upload_form(self):
        form = CandidateCVUploadForm(
            files={
                'cv': self.image,
            }
        )

        self.assertTrue(form.is_valid())


class UserNoteFormTests(BaseTest):

    def setUp(self):
        super(UserNoteFormTests, self).setUp()

    def test_valid_user_note_form_create(self):
        form = UserNoteForm(
            data={
                'note_to': self.user_agent.pk,
                'text': 'test note',
                'type': UserNote.TYPE_TEXT,
            },
            initial={
                'user': self.user_candidate,
            }
        )

        self.assertTrue(form.is_valid())

        user_note = form.save()

        self.assertTrue(user_note)

    def test_invalid_user_note_form_create(self):
        form = UserNoteForm(
            data={},
            initial={
                'user': self.user_candidate,
            }
        )

        self.assertFalse(form.is_valid())

    def test_valid_user_note_form_update(self):
        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        form = UserNoteForm(
            instance=user_note,
            data={
                'note_to': self.user_agent.pk,
                'text': 'test note',
                'type': UserNote.TYPE_TEXT,
            }
        )

        self.assertTrue(form.is_valid())

        user_note = form.save()

        self.assertTrue(user_note)

    def test_invalid_user_note_form_update(self):
        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        form = UserNoteForm(
            instance=user_note,
            data={}
        )

        self.assertFalse(form.is_valid())
