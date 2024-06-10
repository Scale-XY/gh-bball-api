from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Supply Chain Platform API.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore
    position = models.CharField(max_length=255, blank=True, null=True, default=None)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()



class PasswordResetToken(models.Model):
    class Meta:
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=255)
    
    
class UserInvitation(models.Model):
    class Meta:
        verbose_name = _("User Invitation")
        verbose_name_plural = _("User Invitations")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_invited')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_by')
    key = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=255)