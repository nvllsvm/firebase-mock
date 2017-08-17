from firebasemock import helpers
from firebasemock.handlers import base


class GenerateHandler(base.BaseHandler):
    function_map = {
        'authorization': helpers.generate_authorization_key,
        'fcm': helpers.generate_fcm_token,
        'apns': helpers.generate_apns_token,
        'application': helpers.generate_application_name
    }

    def get(self, name):
        value = self.function_map[name]()
        self.shared[name].add(value)
        self.write(value)


class ResetHandler(base.BaseHandler):
    def get(self):
        self.application.shared = helpers.new_shared_state()
