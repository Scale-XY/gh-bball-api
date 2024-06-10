import os
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from io import StringIO


class TestCreateSuperuserCommand(TestCase):
    def setUp(self):
        self.out = StringIO()
        self.user_model = get_user_model()

    def test_superuser_creation(self):
        email = os.environ.get("SUPERUSER_EMAIL", "admin@gh_bball.com")
        password = os.environ.get("SUPERUSER_PASSWORD", "!Qaz2wsx")

        # Ensure the superuser does not exist initially
        self.assertFalse(self.user_model.objects.filter(email=email).exists())

        # Call the management command
        call_command("create_default_superuser", stdout=self.out)

        # Check if the superuser is created
        self.assertTrue(self.user_model.objects.filter(email=email).exists())

        # Check the success message in the output
        expected_output = "Superuser created successfully"
        self.assertIn(expected_output, self.out.getvalue())

    def test_superuser_already_exists(self):
        email = os.environ.get("SUPERUSER_EMAIL", "admin@gh_bball.com")
        password = os.environ.get("SUPERUSER_PASSWORD", "!Qaz2wsx")

        # Create a superuser before running the command
        self.user_model.objects.create_superuser(email, password)

        # Call the management command
        call_command("create_default_superuser", stdout=self.out)

        # Check if the superuser already exists message is in the output
        expected_output = "Superuser already exists"
        self.assertIn(expected_output, self.out.getvalue())
