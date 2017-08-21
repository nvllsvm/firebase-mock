from unittest import mock
import json
import unittest

from tornado import testing

from firebasemock import app, helpers
from firebasemock.handlers import firebase, iid


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
        self.shared = self._app.shared
        helpers.new_shared_state(self.shared)

    def get_auth_header(self):
        key = 'test'
        self.shared['authorization'].add(key)
        return f'key={key}'


class AdminTests(BaseTest):
    def get_app(self):
        return app.make_mock_admin_app()

    def test_default_keys(self):
        for key in ('authorization', 'fcm', 'apns'):
            self.assertIn(f'firebasemock_{key}', self.shared[key])

    def test_token_generation(self):
        for key in ('authorization', 'fcm', 'apns'):
            response = self.fetch(f'/generate/{key}')
            self.assertEqual(response.code, 200)
            self.assertIn(response.text, self.shared[key])

    def test_add_multiple_tokens(self):
        tokens = set([self.fetch('/generate/fcm').text for i in range(3)])
        for token in tokens:
            self.assertIn(token, self.shared['fcm'])

    def test_reset(self):
        self.shared['fcm'].add('testsauce')
        new_state = helpers.new_shared_state()
        original_id = id(self.shared)
        self.assertNotEqual(self.shared, new_state)
        self.fetch('/reset')
        self.assertEqual(self.shared, new_state)
        self.assertEqual(original_id, id(self.shared))

    def test_get_sent_messages(self):
        def get_messages(expected):
            self.assertEqual(self.fetch('/messages').json, expected)

        get_messages({'messages': []})

        expected = [{'to': 'me'},
                    {'to': 'you'}]
        self.shared['messages'] = expected
        get_messages({'messages': expected})

        get_messages({'messages': []})


class IIDTests(BaseTest):
    def get_app(self):
        return app.make_mock_iid_app()

    def test_encoding(self):
        response = self.fetch('/iid/v1%3AbatchImport', method='POST',
                              headers={}, body='')
        self.assertEqual(response.code, 401)

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

        self.shared['apns'] = ['abc']
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
        self.assertIn(mock_token.return_value, self.shared['fcm'])


class FirebaseTests(BaseTest):
    def get_app(self):
        return app.make_mock_firebase_app()

    def request(self, body, headers=None):
        return self.fetch('/fcm/send', method='POST', body=body,
                          headers=headers or {})

    def validate_error(self, response, status_code, body):
        self.assertEqual(response.code, status_code)
        self.assertEqual(response.text, body)

    @mock.patch('firebasemock.helpers.generate_multicast_id')
    def test_invalid_fcm_token(self, multicast_mock):
        multicast_mock.return_value = 123
        response = self.request(
            json.dumps({'to': 'xxx'}),
            headers={'Authorization': self.get_auth_header()})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.json, {
            'canonical_ids': 0,
            'failure': 1,
            'success': 0,
            'multicast_id': multicast_mock.return_value,
            'results': [{'error': 'InvalidRegistration'}]
        })

    @mock.patch('firebasemock.helpers.generate_message_id')
    @mock.patch('firebasemock.helpers.generate_multicast_id')
    def test_send_message(self, multicast_mock, message_mock):
        token = 'aabbccdd'
        self.shared['fcm'].add(token)

        multicast_mock.return_value = 123
        message_mock.return_value = 456
        payload = {'to': token}
        response = self.request(
            json.dumps(payload),
            headers={'Authorization': self.get_auth_header()})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.json, {
            'canonical_ids': 0,
            'failure': 0,
            'success': 1,
            'multicast_id': multicast_mock.return_value,
            'results': [{'message_id': message_mock.return_value}]
        })
        self.assertEqual(self.shared['messages'], [payload])

    def test_no_body(self):
        response = self.request(
            '', headers={'Authorization': self.get_auth_header()})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.text, 'Error=MissingRegistration')

    def test_missing_authorization_header(self):
        response = self.request('')
        self.validate_error(
            response, 401,
            firebase.SendMessageHandler.missing_authorization)

    def test_invalid_authorization_header(self):
        self.validate_error(
            self.request('', headers={'Authorization': 'ha'}),
            401,
            firebase.SendMessageHandler.missing_authorization)

    def test_auth_splits_to_not_key(self):
        self.validate_error(
            self.request('', headers={'Authorization': 'no=no'}),
            401,
            firebase.SendMessageHandler.missing_authorization)

    def test_invalid_authorization_key(self):
        self.validate_error(
            self.request('', headers={'Authorization': 'key=no'}),
            401,
            firebase.SendMessageHandler.invalid_authorization)

    def test_none_token(self):
        self.validate_error(
            self.request(
                json.dumps({'to': None}),
                headers={'Authorization': self.get_auth_header()}),
            400, 'to')

    def test_nonstring_token(self):
        self.validate_error(
            self.request(
                json.dumps({'to': 3}),
                headers={'Authorization': self.get_auth_header()}),
            400, 'Field "to" must be a JSON string: 3')


class HelperTests(unittest.TestCase):
    def test_generate_message_id(self):
        self.validate_output(str, helpers.generate_message_id)

    def test_generate_apns_token(self):
        self.validate_output(str, helpers.generate_apns_token)

    def test_generate_application_name(self):
        self.validate_output(str, helpers.generate_application_name)

    def test_generate_fcm_token(self):
        self.validate_output(str, helpers.generate_fcm_token)

    def test_generate_multicast_id(self):
        self.validate_output(int, helpers.generate_multicast_id)

    def validate_output(self, output_type, function):
        output = function()
        self.assertIsInstance(output, output_type)
        self.assertGreater(len(str(output)), 0)
