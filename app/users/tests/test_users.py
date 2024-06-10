import pytest, pytz
from django.conf import settings
from model_bakery import baker
from random import choice
from rest_framework import status
from users.models import User, PasswordResetToken, UserInvitation


@pytest.mark.django_db
class TestListUser:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        response = api_client.get("/api/users/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_nonadmin_is_authenticated_returns_403(self, authenticate, api_client):
        user = baker.make(User, is_staff=False)
        authenticate(user=user)
        response = api_client.get("/api/users/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_admin_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User, is_staff=True)
        authenticate(user=user)
        response = api_client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        # is_staff/admin users can't view users list
        assert len(response.data) == 0

    def test_if_superadmin_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User, is_superuser=True)
        authenticate(user=user)
        response = api_client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        # since we created a superuser, then users list should be more than 0
        assert len(response.data) > 0


@pytest.mark.django_db
class TestRetrieveUser:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        user = baker.make(User)
        response = api_client.get(f"/api/users/{user.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_anonymous_returns_401_for_ME(self, api_client):
        response = api_client.get(f"/api/users/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        response = api_client.get(f"/api/users/{user.id}/")

        user_groups = list(user.groups.all()) if user.groups.exists() else []

        # Assuming user.date_joined is already in UTC. If it's in a different timezone, adjust accordingly.
        utc_datetime = user.date_joined.replace(tzinfo=pytz.UTC)

        # Convert to the desired timezone
        desired_timezone = pytz.timezone(settings.TIME_ZONE)
        localized_datetime = utc_datetime.astimezone(desired_timezone)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "date_joined": localized_datetime.isoformat(),
            "last_login": user.last_login,
            "groups": [{"id": group.id, "name": group.name} for group in user_groups],
            "position": user.position
        }

    def test_if_user_is_authenticated_returns_200_for_ME(
        self, authenticate, api_client
    ):
        user = baker.make(User)
        authenticate(user=user)
        response = api_client.get(f"/api/users/me/")

        user_groups = list(user.groups.all()) if user.groups.exists() else []

        # Assuming user.date_joined is already in UTC. If it's in a different timezone, adjust accordingly.
        utc_datetime = user.date_joined.replace(tzinfo=pytz.UTC)

        # Convert to the desired timezone
        desired_timezone = pytz.timezone(settings.TIME_ZONE)
        localized_datetime = utc_datetime.astimezone(desired_timezone)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "date_joined": localized_datetime.isoformat(),
            "last_login": user.last_login,
            "groups": [{"id": group.id, "name": group.name} for group in user_groups],
            "position": user.position
        }

    def test_if_authenticated_user_accessed_other_user_record_returns_403(
        self, authenticate, api_client
    ):
        users = baker.make(User, _quantity=2)
        authenticate(user=users[0])
        response = api_client.get(f"/api/users/{users[1].id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {
            "detail": "You do not have permission to perform this action."
        }

    def test_if_superuser_accessed_other_user_record_returns_200(
        self, authenticate, api_client
    ):
        superuser = baker.make(User, is_superuser=True)
        user = baker.make(User)
        authenticate(user=superuser)
        response = api_client.get(f"/api/users/{user.id}/")

        user_groups = list(user.groups.all()) if user.groups.exists() else []

        # for displaying date_joined in the correct format in str
        utc_datetime = user.date_joined.replace(tzinfo=pytz.UTC)
        desired_timezone = pytz.timezone(settings.TIME_ZONE)
        localized_datetime = utc_datetime.astimezone(desired_timezone)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "date_joined": localized_datetime.isoformat(),
            "last_login": user.last_login,
            "groups": [{"id": group.id, "name": group.name} for group in user_groups],
            "position": user.position
        }


@pytest.mark.django_db
class TestCreateUser:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post(
            "/api/users/create_user/",
            {
                "name": "test user",
                "email": "testuser@domain.com",
                "groups": [],
                "is_staff": False,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        response = api_client.post(
            "/api/users/create_user/",
            {
                "name": "test user",
                "email": "testuser@domain.com",
                "groups": [],
                "is_staff": False,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

    # def test_if_user_already_invited_returns_406(self, authenticate, api_client):
    #     inviter = baker.make(User)
    #     authenticate(user=inviter)
    #     user = baker.prepare(User)
    #     key = "".join(
    #         [
    #             choice(
    #                 "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    #             )
    #             for i in range(99)
    #         ]
    #     )
    #     baker.make(
    #         UserInvitation,
    #         user=user,
    #         key=key,
    #         invited_by=inviter,
    #         url="{}?token={}".format(f"{settings.FRONTEND_HOST_URL}/set-account", key),
    #         _quantity=2,
    #     )
    #     response = api_client.post(
    #         "/api/users/create_user/",
    #         {
    #             "name": user.name,
    #             "email": user.email,
    #             "is_staff": user.is_staff,
    #             "groups": [],
    #         },
    #     )

    #     print(response.data)
    #     assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    #     assert "has already been sent a password reset link" in response.data["message"]

    def test_if_data_is_invalid_returns_400(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        response = api_client.post(
            "/api/users/create_user/",
            {
                "name": "Test User",
                "email": "invalid email",
                "is_staff": False,
                "groups": [],
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"email": ["Enter a valid email address."]}


@pytest.mark.django_db
class TestUpdateUser:
    """Here I only tested /api/users/<id>/ since PUT/PATCH methods are not supported on /api/users/me/ endpoint."""

    def test_if_user_is_anonymous_returns_401(self, api_client):
        user = baker.make(User)

        user_groups = list(user.groups.all()) if user.groups.exists() else []

        response = api_client.put(
            f"/api/users/{user.id}/",
            {
                "id": user.id,
                "email": user.email,
                "name": "+",
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "date_joined": user.date_joined,
                "last_login": "",
                "groups": user.groups.all(),
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)

        user_groups = list(user.groups.all()) if user.groups.exists() else []

        response = api_client.put(
            f"/api/users/{user.id}/",
            {
                "id": user.id,
                "email": user.email,
                "name": "+",
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "date_joined": user.date_joined,
                "last_login": "",
                "groups": [
                    {"id": group.id, "name": group.name} for group in user_groups
                ],
            },
        )

        # for displaying date_joined in the correct format in str
        utc_datetime = user.date_joined.replace(tzinfo=pytz.UTC)
        desired_timezone = pytz.timezone(settings.TIME_ZONE)
        localized_datetime = utc_datetime.astimezone(desired_timezone)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": user.id,
            "email": user.email,
            "name": "+",
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "date_joined": localized_datetime.isoformat(),
            "last_login": user.last_login,
            "groups": [{"id": group.id, "name": group.name} for group in user_groups],
            "position": user.position
        }

    def test_if_superuser_updates_other_user_record_returns_200(
        self, authenticate, api_client
    ):
        superuser = baker.make(User, is_superuser=True)
        user = baker.make(User)
        authenticate(user=superuser)
        user_groups = list(user.groups.all()) if user.groups.exists() else []

        response = api_client.put(
            f"/api/users/{user.id}/",
            {
                "id": user.id,
                "email": user.email,
                "name": f"+{user.name}",
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "date_joined": user.date_joined,
                "last_login": "",
                "groups": [],
            },
        )

        # for displaying date_joined in the correct format in str
        utc_datetime = user.date_joined.replace(tzinfo=pytz.UTC)
        desired_timezone = pytz.timezone(settings.TIME_ZONE)
        localized_datetime = utc_datetime.astimezone(desired_timezone)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": user.id,
            "email": user.email,
            "name": f"+{user.name}",
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "date_joined": localized_datetime.isoformat(),
            "last_login": user.last_login,
            "groups": [{"id": group.id, "name": group.name} for group in user_groups],
            "position": user.position
        }


# @pytest.mark.django_db
# class TestDeleteUser:
#     def test_if_nonsuperuser_returns_405(self, authenticate, api_client):
#         user = baker.make(User)
#         authenticate(user=user)
#         response = api_client.delete(f"/api/users/{user.id}/")

#         assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

#     def test_if_superuser_returns_204(self, authenticate, api_client):
#         user = baker.make(User, is_superuser=True)
#         authenticate(user=user)
#         response = api_client.delete(f"/api/users/{user.id}/")

#         assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestExtraActions:
    def test_if_user_is_anonymous_return_401(self, api_client):
        response = api_client.get("/api/users/all_emails/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_200(self, authenticate, api_client):
        authenticate()
        response = api_client.get("/api/users/all_emails/")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUpdatePassword:
    # --------------------- FOR /change-password/ --------------------------------
    def test_change_password_if_user_is_anonymous_returns_401(self, api_client):
        user = baker.make(User)
        user.set_password("24MMGDQgsr")
        response = api_client.put(
            "/api/users/change-password/",
            {
                "old_password": "24MMGDQgsr",
                "new_password1": "+24MMGDQgsr",
                "new_password2": "+24MMGDQgsr",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_if_user_is_authenticated_returns_200(
        self, authenticate, api_client
    ):
        user = baker.make(User)
        user.set_password("24MMGDQgsr")
        authenticate(user=user)
        response = api_client.put(
            "/api/users/change-password/",
            {
                "old_password": "24MMGDQgsr",
                "new_password1": "+24MMGDQgsr",
                "new_password2": "+24MMGDQgsr",
            },
        )

        assert response.status_code == status.HTTP_200_OK

    # ----------------------------------------------------------------------------

    # -------------------- FOR /reset-password/request/ --------------------------
    def test_reset_password_request_if_user_is_anonymous_returns_200(self, api_client):
        user = baker.make(User)
        response = api_client.post(
            "/api/users/reset-password/request/", {"email": user.email}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_reset_password_request_if_user_is_authenticated_returns_200(
        self, authenticate, api_client
    ):
        user = baker.make(User)
        authenticate(user=user)
        response = api_client.post(
            "/api/users/reset-password/request/", {"email": user.email}
        )

        assert response.status_code == status.HTTP_200_OK

    # ----------------------------------------------------------------------------

    # -------------------- FOR /reset-password/confirm/ --------------------------
    def test_reset_password_confirm_if_user_is_anonymous_returns_200(self, api_client):
        user = baker.make(User)
        # for creating a valid PasswordResetToken obj
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
            f"/api/users/reset-password/confirm/?token={key}",
            {
                "new_password1": "24MMGDQgsr",
                "new_password2": "24MMGDQgsr",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"success": "Password updated successfully."}

    def test_reset_password_confirm_if_user_is_authenticated_returns_200(
        self, authenticate, api_client
    ):
        user = baker.make(User)
        authenticate(user=user)
        # for creating a valid PasswordResetToken obj
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
            f"/api/users/reset-password/confirm/?token={key}",
            {
                "new_password1": "24MMGDQgsr",
                "new_password2": "24MMGDQgsr",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"success": "Password updated successfully."}

    # ----------------------------------------------------------------------------

    # -------------------------- FOR /set-account/ -------------------------------
    def test_set_account_if_user_is_anonymous_returns_200(self, api_client):
        users = baker.make(User, _quantity=2)
        # for creating a valid UserInvitation obj
        key = "".join(
            [
                choice(
                    "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
                )
                for i in range(99)
            ]
        )
        baker.make(
            UserInvitation,
            user=users[0],
            key=key,
            invited_by=users[1],
            url="{}?token={}".format(f"{settings.FRONTEND_HOST_URL}/set-account", key),
        )

        response = api_client.post(
            f"/api/users/set-account/?token={key}",
            {"password": "24MMGDQgsr", "confirm_password": "24MMGDQgsr"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"success": "Password updated successfully."}

    def test_set_account_if_user_is_authenticated_returns_200(
        self, authenticate, api_client
    ):
        users = baker.make(User, _quantity=2)
        authenticate(user=users[0])
        # for creating a valid PasswordResetToken obj
        key = "".join(
            [
                choice(
                    "!@$_-qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
                )
                for i in range(99)
            ]
        )
        baker.make(
            UserInvitation,
            user=users[0],
            key=key,
            invited_by=users[1],
            url="{}?token={}".format(f"{settings.FRONTEND_HOST_URL}/set-account", key),
        )

        response = api_client.post(
            f"/api/users/set-account/?token={key}",
            {"password": "24MMGDQgsr", "confirm_password": "24MMGDQgsr"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"success": "Password updated successfully."}

    # ----------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateToken:
    def test_if_user_does_not_exists_returns_401(self, api_client):
        response = api_client.post(
            "/api/users/token/",
            {"email": "testuser@domain.com", "password": "24MMGDQgsr"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {
            "detail": "No active account found with the given credentials"
        }

    def test_if_user_exists_returns_200(self, api_client):
        user = baker.make(User)
        user.set_password("24MMGDQgsr")
        user.save()
        response = api_client.post(
            "/api/users/token/", {"email": user.email, "password": "24MMGDQgsr"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["access"] != None
        assert response.data["refresh"] != None

    # --------------------FOR /api/users/token/refresh/---------------------
    def test_if_refresh_token_is_invalid_returns_401(self, api_client):
        response = api_client.post("/api/users/token/refresh/", {"refresh": "+"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid",
        }

    def test_if_refresh_token_is_valid_returns_200(self, api_client):
        # for creating a user and initial login to get a refresh token
        user = baker.make(User)
        user.set_password("24MMGDQgsr")
        user.save()
        initial_response = api_client.post(
            "/api/users/token/", {"email": user.email, "password": "24MMGDQgsr"}
        )

        response = api_client.post(
            "/api/users/token/refresh/", {"refresh": initial_response.data["refresh"]}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["access"] != None

    # ----------------------------------------------------------------------
