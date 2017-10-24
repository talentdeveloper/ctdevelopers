from django.db.models import Q

from django.views.generic import (
    View
)

from chat.models import (
    Conversation,
)

from braces.views import LoginRequiredMixin, JSONResponseMixin

from .models import (
    Issue,
)


class IssueTrackingAPIView(LoginRequiredMixin, View, JSONResponseMixin):
    """
    View for returning the tracking details of an issue.
    """
    def get(self, *args, **kwargs):
        ''' return issue info as JSON '''
        issue = Issue.objects.get(uuid=self.kwargs.get('uuid'))
        # TODO: check that issue exists

        data = issue.as_dict()
        data['seconds_left'] = issue.seconds_left()
        return self.render_json_response(data)

issue_tracking = IssueTrackingAPIView.as_view()


class IssueCloseAPIView(LoginRequiredMixin, View, JSONResponseMixin):
    """
    View to change issue state.
    """
    def get(self, request, *args, **kwargs):
        ''' change issue state, return updated issue info as JSON '''
        issue = Issue.objects.get(uuid=self.kwargs.get('uuid'))

        issue.change_status_to(Issue.STATUS_CLOSE)
        data = issue.as_dict()
        return self.render_json_response(data)

issue_close = IssueCloseAPIView.as_view()


class ConversationIssuesAPIView(LoginRequiredMixin, View, JSONResponseMixin):
    def get(self, request, *args, **kwargs):
        ''' return information about specific conversation with pk '''
        conversation = Conversation.objects.filter(pk=self.kwargs.get('pk'))
        if not conversation.exists():
            return self.render_json_response({})

        conversation = conversation[0]
        if not conversation.users.filter(pk=request.user.pk).exists():
            return self.render_json_response(
                dict(error='You are not allowed to access this item'),
                status=403
            )

        this_user = request.user
        other_user = conversation.users.filter(~Q(pk=this_user.pk))
        lookup = (Q(provider=this_user) & Q(client=other_user))
        lookup |= (Q(provider=other_user) & Q(client=this_user))
        issues = Issue.objects.filter(lookup)
        if issues.count() >= 1:
            return self.render_json_response({
                'conversation': conversation.pk,
                'issue': issues.first().as_dict()
            })
        return self.render_json_response([])

issues_for_conversation = ConversationIssuesAPIView.as_view()
