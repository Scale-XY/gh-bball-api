import pytest
from model_bakery import baker
from users.models import User
from django.contrib.auth.hashers import check_password


@pytest.mark.django_db
class TestUserManager:
    def test_create_user_without_email(self):
        password = "testpassword"
        with pytest.raises(ValueError, match="The given email must be set"):
            User.objects.create_user(email="", password=password)

    def test_create_user_defaults(self):
        user = User.objects.create_user(
            email="testuser@domain.com", password="24MMGDQgsr"
        )

        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser_defaults(self):
        user = User.objects.create_superuser(
            email="test@example.com", password="testpassword"
        )

        assert user.is_staff
        assert user.is_superuser

    def test_create_superuser_invalid_extrafields_returns_ValueError(self):
        with pytest.raises(ValueError) as is_staff_error:
            User.objects.create_superuser(
                email="test@example.com", password="testpassword", is_staff=False
            )
        assert str(is_staff_error.value) == "Superuser must have is_staff=True."

        with pytest.raises(ValueError) as is_superuser_error:
            User.objects.create_superuser(
                email="test@example.com",
                password="testpassword",
                is_staff=True,
                is_superuser=False,
            )
        assert str(is_superuser_error.value) == "Superuser must have is_superuser=True."
