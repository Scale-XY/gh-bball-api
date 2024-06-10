import pytest
from django.conf import settings
from django.utils import timezone
from model_bakery import baker
from random import choice
from rest_framework import status
from users.models import User, PasswordResetToken, UserInvitation


@pytest.mark.django_db
class TestSetAccountView:
    def test_set_account_view_invalid_key_returns_404(self, api_client):
        response = api_client.post(
            "/api/users/set-account/?token=1",
            {"password": "samplepassword", "confirm_password": "samplepassword"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "Invalid key"}

    def test_set_account_view_invalid_data_returns_400(self, api_client):
        response = api_client.post(
            "/api/users/set-account/?token=1",
            {"password": "samplepassword1", "confirm_password": "samplepassword2"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestChangePasswordView:
    def test_if_passwords_do_not_match_returns_400(self, authenticate, api_client):
        user = baker.make(User)
        user.set_password("24MMGDQgsr")
        authenticate(user=user)
        response = api_client.put(
            "/api/users/change-password/",
            {
                "old_password": "24MMGDQgsr",
                "new_password1": "24MMGDQgsr1",
                "new_password2": "24MMGDQgsr2",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordResetRequestView:
    def test_if_email_doest_not_exist_returns_406(self, api_client):
        response = api_client.post(
            "/api/users/reset-password/request/", {"email": "testuser@domain.com"}
        )

        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert response.data == {"message": "Email does not exists."}

    def test_if_email_already_sent_returns_406(self, api_client):
        user = baker.make(User)
        key = "".join(
            [
                choice(
                    "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
                )
                for i in range(99)
            ]
        )
        baker.make(
            PasswordResetToken,
            user=user,
            key=key,
            url="{}?token={}".format(
                f"{settings.FRONTEND_HOST_URL}/reset-password", key
            ),
        )

        response = api_client.post(
            "/api/users/reset-password/request/", {"email": user.email}
        )

        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert response.data == {
            "message": f"The e-mail address ({user.email}) has already been sent a password reset link."
        }

    def test_email_is_invalid_returns_406(self, api_client):
        response = api_client.post(
            "/api/users/reset-password/request/", {"email": "invalid email"}
        )
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert response.data == {"email": ["Enter a valid email address."]}


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    def test_if_password_reset_token_is_expired_returns_404(self, api_client):
        user = baker.make(User)
        key = "".join(
            [
                choice(
                    "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
                )
                for i in range(99)
            ]
        )
        baker.make(
            PasswordResetToken,
            user=user,
            key=key,
            timestamp=timezone.now() - timezone.timedelta(minutes=35),
            url="{}?token={}".format(
                f"{settings.FRONTEND_HOST_URL}/reset-password", key
            ),
        )

        response = api_client.post(
            f"/api/users/reset-password/confirm/?token={key}",
            {"new_password1": "samplepassword", "new_password2": "samplepassword"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {
            "error": "Password reset key is expired! Reset your email again."
        }

    def test_if_key_is_invalid_returns_404(self, api_client):
        response = api_client.post(
            "/api/users/reset-password/confirm/?token=1",
            {"new_password1": "samplepassword", "new_password2": "samplepassword"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "Invalid key"}

    def test_if_data_is_invalid_returns_400(self, api_client):
        user = baker.make(User)
        key = "".join(
            [
                choice(
                    "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
                )
                for i in range(99)
            ]
        )
        baker.make(
            PasswordResetToken,
            user=user,
            key=key,
            timestamp=timezone.now() - timezone.timedelta(minutes=30),
            url="{}?token={}".format(
                f"{settings.FRONTEND_HOST_URL}/reset-password", key
            ),
        )
        response = api_client.post(
            f"/api/users/reset-password/confirm/?token={key}",
            {"new_password1": "samplepassword1", "new_password2": "samplepassword2"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "new_password2": ["The two password fields didn't match."]
        }


# @pytest.mark.django_db
# class TestUserViewSet:
#     def test_if_email_already_sent_returns_406(self, authenticate, api_client):
#         requester = baker.make(User)
#         user = baker.prepare(User)
#         authenticate(user=requester)
#         key = "".join(
#             [
#                 choice(
#                     "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
#                 )
#                 for i in range(99)
#             ]
#         )
#         baker.make(
#             UserInvitation,
#             user=user,
#             key=key,
#             invited_by=requester,
#             url="{}?token={}".format(f"{settings.FRONTEND_HOST_URL}/set-account", key),
#         )

#         response = api_client.post(
#             "/api/users/create_user/",
#             {
#                 "name": user.name,
#                 "email": user.email,
#                 "groups": [],
#                 "is_staff": False,
#             },
#         )

#         print(response.data)
#         assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
#         assert response.data == {
#             "message": f"The e-mail address ({user.email}) has already been sent a password reset link."
#         }
