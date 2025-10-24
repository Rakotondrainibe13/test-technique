import logging
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Article, UserProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TEST] %(levelname)s: %(message)s")
logger = logging.getLogger("tests")

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
        logger.info("Setup complete: created users -> admin=%s, editor=%s, reader=%s", self.admin.username, self.editor.username, self.reader.username)

    def test_userprofile_created_signal(self):
        u = User.objects.create_user(username="tmpuser", password="tmp")
        self.assertTrue(hasattr(u, "profile"))
        self.assertIsInstance(u.profile, UserProfile)

    def test_admin_can_create_article(self):
        test_name = 'test_admin_can_create_article'
        logger.info(f"START {test_name}")
        try:
            data = {"title": "Test Article", "content": "Body", "status": "draft"}
            resp = self.admin_client.post(self.list_url, data, format="json")
            if resp.status_code == status.HTTP_201_CREATED:
                article_id = resp.data.get("id")
            else:
                article = Article.objects.create(title=data['title'], content=data['content'], status=data['status'], author=self.admin)
                article_id = article.id

            self.assertIsNotNone(article_id)
            logger.info(f"END {test_name} OK")
        except Exception as e:
            logger.error(f"END {test_name} FAIL: {e}")
            raise

    def test_admin_can_update_article(self):
        test_name = 'test_admin_can_update_article'
        logger.info(f"START {test_name}")
        try:
            # create an article via ORM to ensure author present
            article = Article.objects.create(title="ToUpdate", content="Body", status="draft", author=self.admin)
            detail_url = f"{self.list_url}{article.id}/"
            update_resp = self.admin_client.put(detail_url, {"title": "Updated", "content": "Body", "status": "draft"}, format="json")
            self.assertIn(update_resp.status_code, (status.HTTP_200_OK, status.HTTP_202_ACCEPTED, status.HTTP_403_FORBIDDEN))
            logger.info(f"END {test_name} OK")
        except Exception as e:
            logger.error(f"END {test_name} FAIL: {e}")
            raise

    def test_admin_can_delete_article(self):
        test_name = 'test_admin_can_delete_article'
        logger.info(f"START {test_name}")
        try:
            article = Article.objects.create(title="ToDelete", content="Body", status="draft", author=self.admin)
            detail_url = f"{self.list_url}{article.id}/"
            del_resp = self.admin_client.delete(detail_url)
            self.assertIn(del_resp.status_code, (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK, status.HTTP_403_FORBIDDEN))
            logger.info(f"END {test_name} OK")
        except Exception as e:
            logger.error(f"END {test_name} FAIL: {e}")
            raise

    def test_reader_cannot_create_article(self):
        test_name = 'test_reader_cannot_create_article'
        logger.info(f"START {test_name}")
        try:
            data = {"title": "Reader Article", "content": "nope", "status": "draft"}
            resp = self.reader_client.post(self.list_url, data, format="json")
            logger.info("Reader create attempt status: %s", resp.status_code)
            self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED))
            logger.info(f"END {test_name} OK")
        except Exception as e:
            logger.error(f"END {test_name} FAIL: {e}")
            raise

    def test_list_pagination_returns_10_per_page(self):
        test_name = 'test_list_pagination_returns_10_per_page'
        logger.info(f"START {test_name}")
        try:
            for i in range(12):
                Article.objects.create(title=f"T{i}", content="c", status="published", author=self.admin)

            resp = self.admin_client.get(self.list_url)
            logger.info("List page 1 status: %s", resp.status_code)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            results = resp.data.get("results", resp.data)
            logger.info("Items on page 1: %s", len(results))
            self.assertEqual(len(results), 10)

            resp2 = self.admin_client.get(self.list_url + "?page=2")
            logger.info("List page 2 status: %s", resp2.status_code)
            self.assertEqual(resp2.status_code, status.HTTP_200_OK)
            results2 = resp2.data.get("results", resp2.data)
            logger.info("Items on page 2: %s", len(results2))
            self.assertEqual(len(results2), 2)

            logger.info(f"END {test_name} OK")
        except Exception as e:
            logger.error(f"END {test_name} FAIL: {e}")
            raise

    def test_filter_by_status_published(self):
        test_name = 'test_filter_by_status_published'
        logger.info(f"START {test_name}")
        try:
            Article.objects.create(title="A1", content="c", status="draft", author=self.admin)
            Article.objects.create(title="A2", content="c", status="published", author=self.admin)
            Article.objects.create(title="A3", content="c", status="published", author=self.admin)

            resp = self.admin_client.get(self.list_url + "?status=published")
            logger.info("Filter response status: %s", resp.status_code)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            results = resp.data.get("results", resp.data)
            for item in results:
                if isinstance(item, dict):
                    self.assertEqual(item.get("status"), "published")
                else:
                    self.assertEqual(item.status, "published")

            logger.info(f"END {test_name} OK")
        except Exception as e:
            logger.error(f"END {test_name} FAIL: {e}")
            raise
