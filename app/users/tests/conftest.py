import pytest
from rest_framework.test import APIClient
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(user=None):
        if user:
            return api_client.force_authenticate(user=user)
        return api_client.force_authenticate(user=User())

    return do_authenticate
