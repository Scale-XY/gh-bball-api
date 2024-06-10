import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from model_bakery import baker
from users.models import User


@pytest.mark.django_db
class TestListGroup:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        response = api_client.get("/api/users/groups/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        # create a sample group
        group = baker.make(Group)
        response = api_client.get("/api/users/groups/")

        assert response.status_code == status.HTTP_200_OK
        # regular/staff users doesn't see the list group
        assert len(response.data) == 0

    def test_if_superuser_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User, is_superuser=True)
        authenticate(user=user)
        # create a sample group
        group = baker.make(Group)
        response = api_client.get("/api/users/groups/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0


@pytest.mark.django_db
class TestRetrieveGroup:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        group = baker.make(Group)
        response = api_client.get(f"/api/users/groups/{group.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_404(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        # create a sample group
        group = baker.make(Group)
        response = api_client.get(f"/api/users/groups/{group.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_superuser_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User, is_superuser=True)
        authenticate(user=user)
        # create a sample group
        group = baker.make(Group)
        response = api_client.get(f"/api/users/groups/{group.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"id": group.id, "name": group.name}


@pytest.mark.django_db
class TestCreateGroup:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post("/api/users/groups/", {"name": "test group"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_201(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        group = baker.prepare(Group, id=6)
        response = api_client.post("/api/users/groups/", {"name": group.name})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"id": group.id, "name": group.name}

    def test_if_superuser_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User, is_superuser=True)
        authenticate(user=user)
        group = baker.prepare(Group, id=7)
        response = api_client.post("/api/users/groups/", {"name": group.name})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"id": group.id, "name": group.name}


@pytest.mark.django_db
class TestUpdateGroup:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        group = baker.make(Group)
        response = api_client.put(
            f"/api/users/groups/{group.id}/", {"name": f"+{group.name}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_404(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        group = baker.make(Group)
        response = api_client.put(
            f"/api/users/groups/{group.id}/", {"name": f"+{group.name}"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_superuser_is_authenticated_returns_200(self, authenticate, api_client):
        user = baker.make(User, is_superuser=True)
        authenticate(user=user)
        group = baker.make(Group, name="test group 8")
        response = api_client.put(
            f"/api/users/groups/{group.id}/", {"name": f"+{group.name}"}
        )

        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"id": group.id, "name": f"+{group.name}"}


@pytest.mark.django_db
class TestDeleteGroup:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        group = baker.make(Group)
        response = api_client.delete(f"/api/users/groups/{group.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_404(self, authenticate, api_client):
        user = baker.make(User)
        authenticate(user=user)
        group = baker.make(Group)
        response = api_client.delete(f"/api/users/groups/{group.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_superuser_is_authenticated_returns_204(self, authenticate, api_client):
        user = baker.make(User, is_superuser=True)
        authenticate(user=user)
        group = baker.make(Group)
        response = api_client.delete(f"/api/users/groups/{group.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
