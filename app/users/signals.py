from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings

from .models import PasswordResetToken, UserInvitation

#@receiver(reset_password_token_created) add PasswordResetToken here as sender
@receiver(post_save, sender=PasswordResetToken)
def password_reset_token_created(sender, instance, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': instance.user.name,
        'email': instance.user.email,
        'reset_password_url': instance.url
        
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)

    print(instance.user.email)
    send_mail("Password Reset for {title}".format(title="Some website title"),
            "", #leave message params blank because we send message using html template
            settings.EMAIL_HOST_USER,
            [instance.user.email],
            html_message=email_html_message,
            )
    
    
@receiver(post_save, sender=UserInvitation)
def user_invitation_created(sender, instance, *args, **kwargs):
    # send an e-mail to the user
    context = {
        'invited_user': instance.user.name,
        'invited_by': instance.invited_by.email,
        'email': instance.user.email,
        'set_account_url': instance.url
    }

    # render email text
    email_html_message = render_to_string('email/user_invite.html', context)

    print(instance.user.email)
    send_mail("Set Account details for {title}".format(title="gh_bball Internal ERP"),
            "", #leave message params blank because we send message using html template
            settings.EMAIL_HOST_USER,
            [instance.user.email],
            html_message=email_html_message,
            )