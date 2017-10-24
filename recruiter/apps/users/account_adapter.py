import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


logger = logging.getLogger('console_log')
User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        We're trying to solve different use cases:
        - social account already exists, just go on
        - social account has no email or email is unknown, just go on
        - social account's email exists, link social account to existing user
        """

        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        if 'email' not in sociallogin.account.extra_data:
            return

        # get provider name
        social_provider_name = str(sociallogin.account.provider)

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        ##email_in_db = False  # flag shows email is present in DB
        email = sociallogin.account.extra_data['email'].lower()
        logger.info("EMAIL_1: {}".format(email))
        try:
            email_address = EmailAddress.objects.get(email__iexact=email)
            email_in_db = True
        # if it does not, let allauth take care of this new social account
        except EmailAddress.DoesNotExist:
            logger.info("EmailAddress DoesNotExist")
            return
            ## pass

        # check if email exists in user table, if email found nowhere - ignore
#         if (email_in_db is False and
#                 User.objects.filter(email__iexact=email).exists() is False):
#             logger.info("EMAIL_IN_DB: {} EMAIL_IN_USER: {}".format(email_in_db, User.objects.filter(email__iexact=email).exists()))
#             return

        # if it does, bounce back to the login page
        account = User.objects.get(email=email).socialaccount_set.first()
        logger.info("ACCOUNT: " + str(account))
        if account:
            provider_name = account.provider.capitalize()
        else:
            provider_name = 'E-mail'

        messages.error(request, provider_name +
                       " account associated with " + email +
                       " already exists. Please, log in using existing account and" +
                       " and connect your " + social_provider_name.capitalize() +
                       " account through your profile page.")
        raise ImmediateHttpResponse(redirect('/accounts/login'))


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Restrict generating username from email.
    """
    def populate_username(self, request, user):
        pass


class NoNewUsersAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse

        (Comment reproduced from the overridden method.)
        """
        return False
