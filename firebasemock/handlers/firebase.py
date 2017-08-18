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

        token = data.get('to')
        if token is None:
            self.send_error(400, 'to')
        if not isinstance(token, str):
            self.send_error(400, f'Field "to" must be a JSON string: {token}')

        response = {'canonical_ids': 0,
                    'multicast_id': helpers.generate_multicast_id()}
        if token in self.shared['fcm']:
            response.update({
                'failure': 0,
                'success': 1,
                'results': [{'message_id': helpers.generate_message_id()}]
            })
        else:
            response.update({
                'failure': 1,
                'success': 0,
                'results': [{'error': 'InvalidRegistration'}]
            })

        self.write(response)
