from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Article, UserProfile


User = get_user_model()

class ArticlesAPITest(APITestCase):
    def setUp(self):
        # create users
        self.admin = User.objects.create_user(username="admin", password="adminpass", email="admin@example.com")
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        UserProfile.objects.update_or_create(user=self.admin, defaults={"role": "admin"})

        self.editor = User.objects.create_user(username="editor", password="editorpass", email="editor@example.com")
        UserProfile.objects.update_or_create(user=self.editor, defaults={"role": "editor"})

        self.reader = User.objects.create_user(username="reader", password="readerpass", email="reader@example.com")
        UserProfile.objects.update_or_create(user=self.reader, defaults={"role": "reader"})

        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin)

        self.reader_client = APIClient()
        self.reader_client.force_authenticate(user=self.reader)

        self.list_url = "/api/articles/"

        # Log setup summary

    def test_userprofile_created_signal(self):
        u = User.objects.create_user(username="tmpuser", password="tmp")
        self.assertTrue(hasattr(u, "profile"))
        self.assertIsInstance(u.profile, UserProfile)

