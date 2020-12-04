from django.test import TestCase
from django.urls import reverse


class UrlTests(TestCase):

    def setUp(self):
        # Setup run before every test method.
        pass

    def test_tests(self):
        self.assertEqual(1, 1)

    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_post_gtfs_zip(self):
        # GET requests fail
        response = self.client.get(reverse('post_gtfs'))
        self.assertEqual(response.status_code, 400)

        # POST requests without files fail
        response = self.client.post(reverse('post_gtfs'))
        self.assertEqual(response.status_code, 400)

        # other tests in test_views

    def test_admin(self):
        response = self.client.get(reverse('admin'))
        self.assertEqual(response.status_code, 200)

    def test_view_review_category(self):
        response = self.client.get(reverse('view_review_category'))
        self.assertEqual(response.status_code, 200)

    def test_add_review_category(self):
        response = self.client.get(reverse('add_review_category'))
        self.assertEqual(response.status_code, 200)



