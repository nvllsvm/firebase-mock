from tornado import web


class BaseHandler(web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared = self.application.shared

    def send_error(self, status_code, body):
        self.set_status(status_code)
        self.write(body)
        raise web.Finish
