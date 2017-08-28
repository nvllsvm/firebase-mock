import json

from firebasemock import helpers
from firebasemock.handlers import base


class SendMessageHandler(base.BaseHandler):
    missing_authorization = """
<HTML>
<HEAD>
 <TITLE>The request was missing an Authentication Key (FCM Token). Please,
 refer to section &quot;Authentication&quot; of the FCM documentation, at
 https://firebase.google.com/docs/cloud-messaging/server.</TITLE>
</HEAD>
<BODY BGCOLOR="#FFFFFF" TEXT="#000000">
 <H1>The request was missing an Authentication Key (FCM Token). Please, refer
 to section &quot;Authentication&quot; of the FCM documentation, at
 https://firebase.google.com/docs/cloud-messaging/server.</H1>
<H2>Error 401</H2>
</BODY>
</HTML>
"""

    invalid_authorization = """
<HTML>
<HEAD>
<TITLE>Invalid (legacy) Server-key delivered or Sender is not authorized to
 perform request.</TITLE>
</HEAD>
<BODY BGCOLOR="#FFFFFF" TEXT="#000000">
<H1>Invalid (legacy) Server-key delivered or Sender is not authorized to
 perform request.</H1>
<H2>Error 401</H2>
</BODY>
</HTML>
"""

    def prepare(self):
        try:
            authorization = self.request.headers['Authorization']
        except KeyError:
            self.send_error(401, self.missing_authorization)

        try:
            key, token = authorization.split('=', maxsplit=1)
        except ValueError:
            self.send_error(401, self.missing_authorization)

        if key != 'key':
            self.send_error(401, self.missing_authorization)

        if token not in self.shared['authorization']:
            self.send_error(401, self.invalid_authorization)

    def post(self):
        if not self.request.body:
            self.send_error(200, 'Error=MissingRegistration')

        data = json.loads(self.request.body)

        self.shared['messages'].append(data)

        response = {'canonical_ids': 0,
                    'failure': 0,
                    'success': 0,
                    'results': [],
                    'multicast_id': helpers.generate_multicast_id()}

        for token in self._get_tokens(data):
            if token in self.shared['fcm']:
                response['success'] += 1
                response['results'].append({
                    'message_id': helpers.generate_message_id()})
            elif token in self.shared['unregistered_fcm']:
                response['failure'] += 1
                response['results'].append({
                    'error': 'NotRegistered'})
            else:
                response['failure'] += 1
                response['results'].append({
                    'error': 'InvalidRegistration'})

        self.write(response)

    def _get_tokens(self, data):
        # Firebase error handling is inconsistent...

        to = data.get('to')
        registration_ids = data.get('registration_ids')

        if to is None and registration_ids is None:
            self.send_error(400, 'to')

        if to is not None:
            if not isinstance(to, str):
                self.send_error(400,
                                f'Field "to" must be a JSON string: {to}')
            else:
                tokens = []
                tokens.append(to)

        if registration_ids is not None:
            if not isinstance(registration_ids, list):
                self.send_error(400,
                                '"registration_ids" field cannot be empty')
            else:
                tokens = registration_ids

        if None not in (to, registration_ids):
            self.send_error(
                400,
                'Must use either "registration_ids" field or "to", not both')

        return tokens
