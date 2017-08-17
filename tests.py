import json
from unittest import mock

from tornado import testing

from firebasemock import app, helpers
from firebasemock.handlers import iid


class BaseTest(testing.AsyncHTTPTestCase):
    maxDiff = None

    def fetch(self, *args, **kwargs):
        response = super().fetch(*args, **kwargs)
        try:
            response.text = response.body.decode()
        except Exception:
            pass

        try:
            response.json = json.loads(response.body)
        except Exception:
            pass

        return response

    def setUp(self):
        super().setUp()
        self.fetch('/reset')


class AdminTests(BaseTest):
    def get_app(self):
        return app.make_mock_admin_app()

    def test_token_generation(self):
        for key in ('authorization', 'fcm', 'apns'):
            response = self.fetch(f'/generate/{key}')
            self.assertEqual(response.code, 200)
            self.assertEqual(self._app.shared[key],
                             set([response.text]))

    def test_add_multiple_tokens(self):
        tokens = set([self.fetch(f'/generate/fcm').text for i in range(3)])
        self.assertEqual(self._app.shared['fcm'], tokens)

    def test_reset(self):
        self._app.shared['fcm'].add('testsauce')
        new_state = helpers.new_shared_state()
        self.assertNotEqual(self._app.shared, new_state)
        self.fetch('/reset')
        self.assertEqual(self._app.shared, new_state)


class IIDTests(BaseTest):
    def get_auth_header(self):
        key = 'test'
        self._app.shared['authorization'].add(key)
        return f'key={key}'

    def get_app(self):
        return app.make_mock_iid_app()

    def request(self, body, headers={}):
        response = self.fetch('/iid/v1:batchImport', method='POST',
                              headers=headers, body=body)
        return response

    def test_malformed_request(self):
        body = {'test': ''}
        response = self.request(
            json.dumps(body),
            headers={'Authorization': self.get_auth_header()})
        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.json, iid.BatchImportHandler.error_malformed_request)

    def test_unsupported_content_type(self):
        response = self.request(
            '', headers={'Authorization': self.get_auth_header()})
        self.assertEqual(response.code, 400)
        self.assertEqual(
            response.json, iid.BatchImportHandler.error_content_type)

    def test_missing_authorization_header(self):
        response = self.request('')
        self.assertEqual(response.code, 401)

    def test_malformed_authorization(self):
        response = self.request(
            '', headers={'Authorization': 'nope'})
        self.assertEqual(response.code, 401)
        self.assertEqual(
            response.json, iid.BatchImportHandler.error_authorization)

    def test_invalid_authorization(self):
        response = self.request(
            '', headers={'Authorization': 'key=nope'})
        self.assertEqual(response.code, 401)
        self.assertEqual(
            response.json, iid.BatchImportHandler.error_authorization)

    @mock.patch('firebasemock.helpers.generate_fcm_token')
    def test_tokens(self, mock_token):
        mock_token.return_value = 'idkfa'

        self._app.shared['apns'] = ['abc']
        body = {'application': 'test',
                'sandbox': True,
                'apns_tokens': ['abc', 'def']}
        response = self.request(
            json.dumps(body),
            headers={'Authorization': self.get_auth_header()})
        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.json,
            {'results': [{'apns_token': 'abc',
                          'status': 'OK',
                          'registration_token': mock_token.return_value},
                         {'apns_token': 'def',
                          'status': 'INVALID_ARGUMENT'}]})
