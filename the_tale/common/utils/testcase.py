# coding: utf-8

from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse

from dext.utils import s11n

class TestCase(DjangoTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def request_login(self, email, password='111111'):
        response = self.client.post(reverse('accounts:auth:login'), {'email': email, 'password': password})
        self.check_ajax_ok(response)

    def request_logout(self):
        response = self.client.post(reverse('accounts:auth:logout'))
        self.check_ajax_ok(response)

    def check_html_ok(self, response, status_code=200, texts=[], content_type='text/html'):
        self.assertEqual(response.status_code, status_code)

        self.assertTrue(content_type in response['Content-Type'])

        content = response.content.decode('utf-8')
        for text in texts:
            if isinstance(text, tuple):
                substr, number = text
                self.assertEqual((substr, content.count(substr)), (substr, number))
            else:
                self.assertEqual((text, text in content), (text, True))

    def check_ajax_ok(self, response, data=None, content_type='application/json'):
        self.assertTrue(content_type in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        content = s11n.from_json(response.content)
        self.assertEqual(content['status'], 'ok')

        if data is not None:
            self.assertEqual(content['data'], data)

    def check_ajax_error(self, response, code, content_type='application/json'):
        self.assertTrue(content_type in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        data = s11n.from_json(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], code)

    def check_ajax_processing(self, response, status_url=None, content_type='application/json'):
        self.assertTrue(content_type in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        data = s11n.from_json(response.content)
        self.assertEqual(data['status'], 'processing')
        if status_url:
            self.assertEqual(data['status_url'], status_url)

    def check_redirect(self, requested_url, test_url, status_code=302, target_status_code=200):
        self.assertRedirects(self.client.get(requested_url), test_url, status_code=status_code, target_status_code=target_status_code)


class CallCounter(object):

    def __init__(self):
        self.count = 0

    def __call__(self, *argv, **kwargs):
        self.count += 1
