import json
from tempfile import NamedTemporaryFile

from django.contrib.auth import (
    get_user_model,
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
from recruit.models import Skill
from users.models import (
    Candidate,
    CandidateSkill,
    CVRequest,
    UserNote,
)


User = get_user_model()


class FileUploadAPITests(BaseTest):

    def setUp(self):
        super(FileUploadAPITests, self).setUp()

        image = Image.new('RGB', size=(10, 10))
        file = NamedTemporaryFile(suffix='.jpg')
        image.save(file)
        self.image = File(open(file.name, 'rb'))

    def test_candidate_photo_upload(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:profile_photo_upload'),
            {
                'photo': self.image,
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            }
        )

        self.assertEqual(response.status_code, 200)

        self.candidate.refresh_from_db()
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('image'), self.candidate.photo.url)

    def test_agent_photo_upload(self):
        self.client.login(username=self.user_agent.email, password='agent')

        response = self.client.post(
            reverse('users:profile_photo_upload'),
            {
                'photo': self.image,
                'x': 0,
                'y': 0,
                'width': 10,
                'height': 10,
            }
        )

        self.assertEqual(response.status_code, 200)

        self.agent.refresh_from_db()
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('image'), self.agent.photo.url)

    def test_candidate_cv_upload(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:profile_cv_upload'),
            {
                'cv': self.image,
            }
        )

        self.assertEqual(response.status_code, 200)

        self.candidate.refresh_from_db()
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('cv'), self.candidate.cv.url)


class UserNoteAPITests(BaseTest):

    def setUp(self):
        super(UserNoteAPITests, self).setUp()

    def test_valid_create_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:user_note_create'),
            {
                'note_to': self.user_agent.pk,
                'text': 'test note',
                'type': UserNote.TYPE_TEXT,
            }
        )

        self.assertEqual(response.status_code, 200)

        user_note = UserNote.objects.filter(note_to=self.user_agent, note_by=self.user_candidate).first()
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('data').get('pk'), user_note.pk)

    def test_invalid_create_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:user_note_create'),
            {}
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertFalse(payload.get('success'))

    def test_valid_update_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        response = self.client.post(
            reverse('users:user_note_update', kwargs={'pk': user_note.pk}),
            {
                'note_to': self.user_agent.pk,
                'text': 'test note',
                'type': UserNote.TYPE_TEXT,
            }
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(payload.get('data').get('pk'), user_note.pk)

    def test_invalid_update_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        response = self.client.post(
            reverse('users:user_note_update', kwargs={'pk': user_note.pk}),
            {}
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertFalse(payload.get('success'))

    def test_delete_user_note(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user_note = G(
            UserNote,
            note_by=self.user_candidate,
            note_to=self.user_agent
        )

        response = self.client.post(reverse('users:user_note_delete', kwargs={'pk': user_note.pk}))

        self.assertEqual(response.status_code, 200)

        user_note = UserNote.objects.filter(note_to=self.user_agent, note_by=self.user_candidate)
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertFalse(user_note.exists())


class ProfileAPITests(BaseTest):

    def setUp(self):
        super(ProfileAPITests, self).setUp()

    def test_valid_candidate_profile_detail_update(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:candidate_profile_detail_update', kwargs={'pk': self.candidate.pk}),
            {
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

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))

        skill = Skill.objects.filter(name='skill 1')
        candidate_skill = CandidateSkill.objects.filter(skill=skill, candidate=self.candidate)

        self.assertTrue(skill.exists())
        self.assertTrue(candidate_skill.exists())

    def test_invalid_candidate_profile_detail_update(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        response = self.client.post(
            reverse('users:candidate_profile_detail_update', kwargs={'pk': self.candidate.pk}),
            {}
        )

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)

        self.assertFalse(payload.get('success'))

    def test_tracking_api(self):
        self.client.login(username=self.user_candidate.email, password='candidate')

        user_note = G(
            UserNote,
            note_to=self.user_agent,
            note_by=self.user_candidate
        )

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

        response = self.client.get(reverse('users:tracking', kwargs={'pk': self.user_agent.pk}))

        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        data = payload.get('data')

        user_notes = data.get('user_notes')

        self.assertTrue(user_notes)
        self.assertEqual(user_notes[0].get('pk'), user_note.pk)

        auto_tracking = data.get('auto_tracking')

        self.assertEqual(auto_tracking.get('first_contact_sent'), message_agent.created_at.strftime('%d/%m/%y'))
        self.assertEqual(auto_tracking.get('last_message_sent'), message_agent.created_at.strftime('%d/%m/%y'))
        self.assertEqual(auto_tracking.get('last_message_received'), message_candidate.created_at.strftime('%d/%m/%y'))

class CVRequestAPITests(BaseTest):

    def setUp(self):
        super(CVRequestAPITests, self).setUp()

    def test_valid_update_cv_request_api(self):
        self.client.login(username=self.user_agent.email, password='agent')

        cv_request = G(
            CVRequest,
            candidate=self.candidate,
            requested_by=self.user_agent,
            status=CVRequest.STATUS_PENDING
        )

        response = self.client.post(
            reverse('users:cv_request_update', kwargs={'uuid': cv_request.uuid}),
            {
                'status': CVRequest.STATUS_APPROVED,
            }
        )

        self.assertEqual(response.status_code, 200)

        cv_request.refresh_from_db()
        payload = json.loads(response.content)

        self.assertTrue(payload.get('success'))
        self.assertEqual(cv_request.status, CVRequest.STATUS_APPROVED)

    def test_invalid_update_cv_request_api(self):
        self.client.login(username=self.user_agent.email, password='agent')

        cv_request = G(
            CVRequest,
            candidate=self.candidate,
            requested_by=self.user_agent,
            status=CVRequest.STATUS_PENDING
        )

        response = self.client.post(
            reverse('users:cv_request_update', kwargs={'uuid': cv_request.uuid}),
            {}
        )

        self.assertEqual(response.status_code, 200)

        cv_request.refresh_from_db()
        payload = json.loads(response.content)

        self.assertFalse(payload.get('success'))
        self.assertTrue(payload.get('errors'))
        self.assertEqual(cv_request.status, CVRequest.STATUS_PENDING)
