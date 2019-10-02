import logging
import sys

import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
import tornado.web

import application
import auth
import settings as portal_settings

define("port", default=5000, help="Run on the given port", type=int)
define("develop", default=False, help="Run in develop environment", type=bool)

# Setup the Tornado Application
# pylint: disable=no-member
tornado_settings = {"debug": False,
                    "cookie_secret": portal_settings.cookie_secret,
                    "login_url": "/login",
                    "elixir_oauth": {
                        "id": portal_settings.elixir["id"],
                        "secret": portal_settings.elixir["secret"],
                        "redirect_uri": portal_settings.elixir["redirectUri"],
                    },
                    "xsrf_cookies": True,
                    "template_path": "templates/"}
# pylint: enable=no-member

# pylint: disable=line-too-long

class Application(tornado.web.Application):
    def __init__(self, settings):
        self.declared_handlers = [
            # Static handlers
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static/"}),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": "static/img/"}),
            # Authentication
            (r"/logout", auth.ElixirLogoutHandler),
            (r"/elixir/login", auth.ElixirLoginHandler),
            (r"/elixir/logout", auth.ElixirLogoutHandler),
            # User-related methods
            (r"/api/countries", application.CountryList),
            (r"/api/users", application.ListUsers),
            (r"/api/users/me", application.GetUser),
            # Dataset methods
            (r"/api/datasets", application.ListDatasets),
            (r"/api/dataset/add", application.AddDataset),
            (r"/api/dataset/delete", application.DeleteDataset),
            (r"/api/dataset/query", application.FindDataset),
            (r"/api/dataset/(?P<ds_identifier>[0-9]+)", application.GetDataset),
        ]

        # Adding Catch all handlers
        self.declared_handlers += [
            (r"/api/.*", tornado.web.ErrorHandler, {"status_code": 404}),
            (r'().*', tornado.web.StaticFileHandler, {"path": "static/templates/", "default_filename": "index.html"}),
            ]

        # Adding developer login handler
        if settings.get('develop', False):
            self.declared_handlers.insert(-1, ("/developer/login", auth.DeveloperLoginHandler))
            self.declared_handlers.insert(-1, ("/developer/quit", application.QuitHandler))

        # Setup the Tornado Application
        tornado.web.Application.__init__(self, self.declared_handlers, **settings)


if __name__ == '__main__':
    # Make sure that the extra option to `settings` isn't upsetting tornado
    if '--settings_file' in sys.argv:
        flag_index = sys.argv.index('--settings_file')
        # first remove flag, then argument
        del sys.argv[flag_index]
        del sys.argv[flag_index]

    tornado.log.enable_pretty_logging()
    tornado.options.parse_command_line()

    if options.develop:
        tornado_settings['debug'] = True
        tornado_settings['develop'] = True
        logging.getLogger().setLevel(logging.DEBUG)

    # Instantiate Application
    tornado_application = Application(tornado_settings)
    tornado_application.listen(options.port, xheaders=True)

    # Get a handle to the instance of IOLoop
    ioloop = tornado.ioloop.IOLoop.instance()

    # Start the IOLoop
    ioloop.start()
