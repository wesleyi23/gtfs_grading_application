from django.test import TestCase
from django.urls import reverse


class ViewTests(TestCase):

    def test_post_gtfs_zip(self):
        # POST with valid GTFS passes
        with open('files_for_testing/BART.zip', 'rb') as file:
            response = self.client.post(reverse('post_gtfs'), {'file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")

        # POST with invalid GTFS fails
        with open('files_for_testing/image_test.jpg', 'rb') as file:
            response = self.client.post(reverse('post_gtfs'), {'file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-danger")