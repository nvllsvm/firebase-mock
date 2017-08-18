from tornado import ioloop
from tornado import web

from firebasemock import helpers
from firebasemock.handlers import admin, firebase, iid


STATE = helpers.new_shared_state()


def make_app(urls):
    app = web.Application(urls)
    app.shared = STATE
    return app


def make_mock_admin_app():
    return make_app([
        ('/generate/(.*)', admin.GenerateHandler),
        ('/messages', admin.MessagesHandler),
        ('/reset', admin.ResetHandler)
    ])


def make_mock_iid_app():
    return make_app([
        ('/iid/v1:batchImport', iid.BatchImportHandler)
    ])


def make_mock_firebase_app():
    return make_app([
        ('/fcm/send', firebase.SendMessageHandler)
    ])


def run():  # pragma: no cover
    admin_app = make_mock_admin_app()
    admin_app.listen(8000)
    iid_app = make_mock_iid_app()
    iid_app.listen(8001)
    firebase_app = make_mock_firebase_app()
    firebase_app.listen(8002)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':  # pragma: no cover
    run()
