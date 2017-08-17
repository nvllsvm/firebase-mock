import json

from tornado import web

from firebasemock import helpers
from firebasemock.handlers import base


class BatchImportHandler(base.BaseHandler):
    error_content_type = {'error': 'Content type not supported'}
    error_malformed_request = {'error': 'Malformed request'}
    error_authorization = {'error': 'Not authenticated or unauthorized'}

    def prepare(self):
        try:
            authorization = self.request.headers['Authorization']
        except KeyError:
            self.send_bad_auth_response()

        try:
            key, token = authorization.split('=', maxsplit=1)
        except ValueError:
            self.send_bad_auth_response()

        if key != 'key' or token not in self.shared['authorization']:
            self.send_bad_auth_response()

    def send_bad_auth_response(self):
        self.write(self.error_authorization)
        self.set_status(401)
        raise web.Finish

    def post(self):
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.write(self.error_content_type)
            self.set_status(400)
            raise web.Finish

        if not data.get('application') or data.get('sandbox') not in (True,
                                                                      False):
            self.write(self.error_malformed_request)
            self.set_status(400)
            raise web.Finish

        results = []
        for token in data['apns_tokens']:
            result = {'apns_token': token}
            if token not in self.shared['apns']:
                result['status'] = 'INVALID_ARGUMENT'
            else:
                fcm_token = helpers.generate_fcm_token()
                self.shared['fcm'] = fcm_token
                result['registration_token'] = fcm_token
                result['status'] = 'OK'

            results.append(result)

        self.write({'results': results})
