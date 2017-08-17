from tornado import ioloop
from tornado import web

from firebasemock import helpers
from firebasemock.handlers import admin, iid


state = helpers.new_shared_state()


def make_app(urls):
    app = web.Application(urls)
    app.shared = state
    return app


def make_mock_admin_app():
    return make_app([
        ('/generate/(.*)', admin.GenerateHandler),
        ('/reset', admin.ResetHandler)
    ])


def make_mock_iid_app():
    return make_app([
        ('/iid/v1:batchImport', iid.BatchImportHandler)
    ])


def run():
    admin_app = make_mock_admin_app()
    admin_app.listen(8000)
    iid_app = make_mock_iid_app()
    iid_app.listen(8001)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    run()
