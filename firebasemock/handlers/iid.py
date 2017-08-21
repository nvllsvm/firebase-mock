import json

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
            self.send_error(401, self.error_authorization)

        try:
            key, token = authorization.split('=', maxsplit=1)
        except ValueError:
            self.send_error(401, self.error_authorization)

        if key != 'key' or token not in self.shared['authorization']:
            self.send_error(401, self.error_authorization)

    def post(self):
        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.send_error(400, self.error_content_type)

        if not data.get('application') or data.get('sandbox') not in (True,
                                                                      False):
            self.send_error(400, self.error_malformed_request)

        results = []
        for token in data['apns_tokens']:
            result = {'apns_token': token}
            if token not in self.shared['apns']:
                result['status'] = 'INVALID_ARGUMENT'
            else:
                fcm_token = helpers.generate_fcm_token()
                self.shared['fcm'].add(fcm_token)
                result['registration_token'] = fcm_token
                result['status'] = 'OK'

            results.append(result)

        self.write({'results': results})
