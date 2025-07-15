from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from experienciaas.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def add_message(self, request, level, message_template, message_context=None, extra_tags=""):
        """
        Override to disable automatic login/logout messages.
        """
        # Don't show login/logout success messages
        if message_template in [
            "account/messages/logged_in.txt", 
            "account/messages/logged_out.txt"
        ]:
            return
        # Call parent method for other messages
        super().add_message(request, level, message_template, message_context, extra_tags)

    def is_email_verification_mandatory(self, request, email_address):
        """
        Override to make email verification mandatory for the primary email only.
        """
        return True

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Override to use custom email confirmation URL if needed.
        """
        return super().get_email_confirmation_url(request, emailconfirmation)

    def send_mail(self, template_prefix, email, context):
        """
        Override to use Spanish email templates.
        """
        # Map template prefixes to Spanish versions
        spanish_templates = {
            "account/email/password_reset_key": "account/email/password_reset_key_es",
            "account/email/email_confirmation": "account/email/email_confirmation_es", 
            "account/email/email_confirmation_signup": "account/email/email_confirmation_es",
            "account/email/account_already_exists": "account/email/account_already_exists_es",
            "account/email/unknown_account": "account/email/unknown_account_es",
        }
        
        # Use Spanish template if available
        spanish_template = spanish_templates.get(template_prefix, template_prefix)
        return super().send_mail(spanish_template, email, context)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
