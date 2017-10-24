from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
)

from braces.views import LoginRequiredMixin


User = get_user_model()


class ProfileCompleteRequiredMixin(LoginRequiredMixin):
    """
    Only allow profile completed users to access this page. Otherwise, redirect them back to their profile page.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if not user.profile.is_initial_profile_complete:
                if user.account_type == User.ACCOUNT_CANDIDATE:
                    return HttpResponseRedirect(reverse_lazy('users:profile_update'))
                elif user.account_type in [User.ACCOUNT_AGENT, User.ACCOUNT_SUPPORT]:
                    return HttpResponseRedirect(
                        '{}?profile={}'.format(
                            reverse_lazy('companies:company_detail', kwargs={'slug': user.profile.company.slug}),
                            user.profile.pk
                        )
                    )

        return super(ProfileCompleteRequiredMixin, self).dispatch(request, *args, **kwargs)


class CandidateRequiredMixin(LoginRequiredMixin):
    """
    Only allow candidates to access this page. Otherwise, redirect them back to their dashboard page.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.account_type == User.ACCOUNT_CANDIDATE:
                if not user.profile.is_initial_profile_complete and not request.is_ajax():
                    return HttpResponseRedirect(
                        reverse_lazy('users:candidate_profile', kwargs={'slug': user.slug})
                    )
            else:
                return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))

        return super(CandidateRequiredMixin, self).dispatch(request, *args, **kwargs)


class AgentRequiredMixin(LoginRequiredMixin):
    """
    Only allow agents to access this page. Otherwise, redirect them back to their dashboard page.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.account_type == User.ACCOUNT_AGENT:
                if not user.profile.is_initial_profile_complete and user.profile.company and not request.is_ajax():
                    return HttpResponseRedirect(
                        '{}?profile={}'.format(
                            reverse_lazy('companies:company_detail', kwargs={'slug': user.profile.company.slug}),
                            user.profile.pk
                        )
                    )
            else:
                return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))

        return super(AgentRequiredMixin, self).dispatch(request, *args, **kwargs)


class SupportTRequiredMixin(LoginRequiredMixin):
    """
    Only allow IT support to access this page. Otherwise, redirect them back to their dashboard page.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.account_type == User.ACCOUNT_SUPPORT:
                if not user.profile.is_initial_profile_complete and user.profile.company and not request.is_ajax():
                    return HttpResponseRedirect(
                        '{}?profile={}'.format(
                            reverse_lazy('companies:company_detail', kwargs={'slug': user.profile.company.slug}),
                            user.profile.pk
                        )
                    )
            else:
                return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))
        return super(SupportTRequiredMixin, self).dispatch(request, *args, **kwargs)


class AgentSupportRequiredMixin(LoginRequiredMixin):
    """
    Only allow agents and IT supports to access this page. Otherwise, redirect them back to their dashboard page.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.account_type in [User.ACCOUNT_AGENT, User.ACCOUNT_SUPPORT]:
                if not user.profile.is_initial_profile_complete and user.profile.company and not request.is_ajax():
                    return HttpResponseRedirect(
                        '{}?profile={}'.format(
                            reverse_lazy('companies:company_detail', kwargs={'slug': user.profile.company.slug}),
                            user.profile.pk
                        )
                    )
            else:
                return HttpResponseRedirect(reverse_lazy('recruit:dashboard'))

        return super(AgentSupportRequiredMixin, self).dispatch(request, *args, **kwargs)
