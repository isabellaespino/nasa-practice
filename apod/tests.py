from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

FAKE_NASA_RESPONSE = {
    "title": "Test Nebula",
    "explanation": "A nebula, for testing purposes.",
    "media_type": "image",
    "url": "https://example.com/test.jpg",
    "date": "2020-01-01",
}


class HomeViewTests(TestCase):
    @patch("apod.services._fetch_from_nasa", return_value=FAKE_NASA_RESPONSE)
    def test_home_page_fetches_and_renders_todays_entry(self, mock_fetch):
        response = self.client.get(reverse("apod:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Nebula")
        mock_fetch.assert_called_once()

    @patch("apod.services._fetch_from_nasa", return_value=FAKE_NASA_RESPONSE)
    def test_home_page_uses_cache_on_second_visit(self, mock_fetch):
        self.client.get(reverse("apod:home"))
        self.client.get(reverse("apod:home"))

        mock_fetch.assert_called_once()


class PastDateViewTests(TestCase):
    @patch("apod.services._fetch_from_nasa", return_value=FAKE_NASA_RESPONSE)
    def test_valid_past_date_renders_entry(self, mock_fetch):
        response = self.client.get(
            reverse("apod:detail", kwargs={"entry_date": "2020-01-01"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Nebula")

    @patch("apod.services._fetch_from_nasa", return_value=FAKE_NASA_RESPONSE)
    def test_future_date_is_rejected_without_calling_api(self, mock_fetch):
        future = (date.today() + timedelta(days=1)).isoformat()

        response = self.client.get(
            reverse("apod:detail", kwargs={"entry_date": future})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "future")
        mock_fetch.assert_not_called()

    def test_malformed_date_shows_error_without_calling_api(self):
        response = self.client.get(
            reverse("apod:detail", kwargs={"entry_date": "not-a-date"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "valid date")


class NavAuthTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice", password="alice-password"
        )

    @patch("apod.services._fetch_from_nasa", return_value=FAKE_NASA_RESPONSE)
    def test_shows_login_link_when_logged_out(self, mock_fetch):
        response = self.client.get(reverse("apod:home"))

        self.assertContains(response, "Login")
        self.assertNotContains(response, "Logout")

    @patch("apod.services._fetch_from_nasa", return_value=FAKE_NASA_RESPONSE)
    def test_shows_logout_and_username_when_logged_in(self, mock_fetch):
        self.client.login(username="alice", password="alice-password")

        response = self.client.get(reverse("apod:home"))

        self.assertContains(response, "Logout")
        self.assertContains(response, "alice")
