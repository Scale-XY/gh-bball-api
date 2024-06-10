import pytest
from django.contrib.auth import password_validation as validators
from django.core import exceptions
from django.http import HttpRequest
from django.utils.translation import gettext as _
from rest_framework import serializers
from utils.mixins import BaseSerializer
from users.serializers import (
    RegisterSerializer,
    SetUserSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
)
from users.models import User


@pytest.mark.django_db
class TestRegisterSerializer:
    def test_create_user(self):
        data = {
            "email": "test@example.com",
            "password": "testpassword",
        }

        serializer = RegisterSerializer(data=data)

        assert serializer.is_valid()

        user = serializer.save()

        assert user is not None
        assert user.email == data["email"]
        assert user.check_password(data["password"])


@pytest.mark.django_db
class TestSetUserSerializer:
    def test_password_fields_do_not_match(self):
        data = {
            "password": "testpassword1",
            "confirm_password": "testpassword2",
        }

        serializer = SetUserSerializer(data=data)

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert _("The two password fields didn't match.") in str(excinfo.value)

    def test_validate_password_exception(self):
        data = {
            "password": "12345678",
            "confirm_password": "12345678",
        }

        serializer = SetUserSerializer(data=data)

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert _("password") in str(excinfo.value)


@pytest.mark.django_db
class TestChangePasswordSerializer:
    def test_validate_old_password_incorrect(self):
        user = User.objects.create_user(
            email="test@example.com", password="oldpassword"
        )

        data = {
            "old_password": "incorrectpassword",
            "new_password1": "newpassword",
            "new_password2": "newpassword",
        }

        request = HttpRequest()
        request.user = user

        serializer = ChangePasswordSerializer(data=data, context={"request": request})

        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        assert _(
            "Your old password was entered incorrectly. Please enter it again."
        ) in str(excinfo.value)

    def test_validate_new_passwords_do_not_match(self):
        # Create a user with a known password
        user = User.objects.create_user(
            email="test@example.com", password="oldpassword"
        )
        authenticated_user = user

        # Test data with mismatched new passwords
        data = {
            "old_password": "oldpassword",
            "new_password1": "newpassword1",
            "new_password2": "newpassword2",
        }

        request = HttpRequest()
        request.user = authenticated_user

        # Create an instance of the serializer with the test data and request context
        serializer = ChangePasswordSerializer(data=data, context={"request": request})

        # Validate the serializer data
        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        # Check if the expected error message is present in the exception
        assert _("The two password fields didn't match.") in str(excinfo.value)

    def test_validate_new_password_same_as_old_password(self):
        # Create a user with a known password
        user = User.objects.create_user(
            email="test@example.com", password="oldpassword"
        )
        authenticated_user = user

        # Test data with the same old and new passwords
        data = {
            "old_password": "oldpassword",
            "new_password1": "oldpassword",
            "new_password2": "oldpassword",
        }

        request = HttpRequest()
        request.user = authenticated_user

        # Create an instance of the serializer with the test data and request context
        serializer = ChangePasswordSerializer(data=data, context={"request": request})

        # Validate the serializer data
        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        # Check if the expected error message is present in the exception
        assert _(
            "Your new password cannot be the same as your last old password."
        ) in str(excinfo.value)


@pytest.mark.django_db
class TestPasswordResetConfirmSerializer:
    def test_validate_new_passwords_do_not_match(self):
        # Test data with mismatched new passwords
        data = {
            "new_password1": "newpassword1",
            "new_password2": "newpassword2",
        }

        # Create an instance of the serializer with the test data
        serializer = PasswordResetConfirmSerializer(data=data)

        # Validate the serializer data
        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        # Check if the expected error message is present in the exception
        assert _("The two password fields didn't match.") in str(excinfo.value)

    def test_validate_password_validation_error(self):
        # Test data with a password that does not meet the validation requirements
        data = {
            "new_password1": "12345678",
            "new_password2": "12345678",
        }

        # Create an instance of the serializer with the test data
        serializer = PasswordResetConfirmSerializer(data=data)

        # Validate the serializer data
        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        # Check if the expected error message is present in the exception
        assert "password" in str(excinfo.value)

    def test_validate_errors_raise_validation_error(self):
        # Test data with a password that does not meet the validation requirements
        data = {
            "new_password1": "12345678",
            "new_password2": "12345678",
        }

        # Create an instance of the serializer with the test data
        serializer = PasswordResetConfirmSerializer(data=data)

        # Mock the exceptions.ValidationError to simulate a password validation error
        with pytest.raises(exceptions.ValidationError) as validation_error:
            validators.validate_password(password=data["new_password1"])

        # Validate the serializer data
        with pytest.raises(serializers.ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        # Check if the expected error message is present in the exception
        assert "password" in str(excinfo.value)
