import logging
import urllib.parse

import peewee
import tornado.auth
import tornado.escape
from tornado.escape import json_encode
import tornado.httpclient
import tornado.web

import db
import utils


class BaseHandler(tornado.web.RequestHandler):
    """
    Base Handler. Handlers should not inherit from this
    class directly but from either SafeHandler or UnsafeHandler
    to make security status explicit.
    """
    def prepare(self):
        # Make sure we have the xsrf_token, this will generate the xsrf cookie if it isn't set
        self.xsrf_token  # pylint: disable=pointless-statement
        if db.database.is_closed():
            try:
                db.database.connect()
            except peewee.DatabaseError as err:
                logging.error(f"Failed to connect to database: {err}")

    def on_finish(self):
        if not db.database.is_closed():
            db.database.close()

    def get_current_user(self):
        email = self.get_secure_cookie('email')
        name = self.get_secure_cookie('user')
        identity = self.get_secure_cookie('identity')

        # Fix ridiculous bug with quotation marks showing on the web
        if name and (name[0] == '"') and (name[-1] == '"'):
            name = name[1:-1]

        if identity:
            try:
                return db.User.select().where(db.User.auth_identity == identity).get()
            except db.User.DoesNotExist:
                # Not saved in the database yet
                try:
                    return db.User(email=email.decode('utf-8'),
                                   name=name.decode('utf-8'),
                                   auth_identity=identity.decode('utf-8'))
                except peewee.OperationalError as err:
                    logging.error(f"Can't create new user: {err}")
        else:
            return None

    def set_user_msg(self, msg, level="info"):
        """
        This function sets the user message cookie. The system takes four default
        levels, 'success', 'info', 'warning', and 'error'. Messages set to other
        levels will be defaulted to 'info'.
        """
        if level not in ["success", "info", "warning", "error"]:
            level = "info"
        self.set_cookie("msg", urllib.parse.quote(json_encode({"msg": msg, "level": level})))

    def write_error(self, status_code, **kwargs):
        """
        Overwrites write_error method to have custom error pages.
        http://tornado.readthedocs.org/en/latest/web.html#tornado.web.RequestHandler.write_error
        """
        logging.info("Error do something here again")

    def write(self, chunk):
        if not isinstance(chunk, dict):
            super().write(chunk)
            return
        new_chunk = _convert_keys_to_hump_back(chunk)
        super().write(new_chunk)


def _convert_keys_to_hump_back(chunk):
    """
    Converts keys given in snake_case to humpBack-case, while preserving the
    capitalization of the first letter.
    """
    if isinstance(chunk, list):
        return [_convert_keys_to_hump_back(e) for e in chunk]

    if not isinstance(chunk, dict):
        return chunk

    new_chunk = {}
    for k, v in chunk.items():
        # First character should be the same as in the original string
        new_key = k[0] + "".join([a[0].upper() + a[1:] for a in k.split("_")])[1:]
        new_chunk[new_key] = _convert_keys_to_hump_back(v)
    return new_chunk


class UnsafeHandler(BaseHandler):
    pass


class SafeHandler(BaseHandler):
    """
    All handlers that need authentication and authorization should inherit
    from this class.
    """
    def prepare(self):
        """
        This method is called before any other method.
        Having the decorator @tornado.web.authenticated here implies that all
        the Handlers that inherit from this one are going to require
        authentication in all their methods.
        """
        super().prepare()
        if not self.current_user:
            logging.debug("No current user: 403")
            self.send_error(status_code=403)


class StewardHandler(SafeHandler):
    """
    All handlers requiring Steward or higher rights should inherit from this class.
    """
    def prepare(self):
        """
        Perform SafeHandler checks as well as check that user is Steward or Admin.
        """
        super().prepare()
        if not utils.has_rights(self.current_user, ('Steward', 'Admin')):
            logging.debug("User does not have Steward or higher permissions: 403")
            self.send_error(status_code=403)

        if self._finished:
            return


class AdminHandler(SafeHandler):
    """
    All handlers requiring Admin rights should inherit from this class.
    """
    def prepare(self):
        """
        Perform SafeHandler checks as well as check that user is Admin.
        """
        super().prepare()
        if not utils.has_rights(self.current_user, ('Admin')):
            logging.debug("User does not have Admin permissions: 403")
            self.send_error(status_code=403)

        if self._finished:
            return


class SafeStaticFileHandler(tornado.web.StaticFileHandler, SafeHandler):
    """
    Serve static files for logged in users
    """


class AngularTemplate(UnsafeHandler):
    def initialize(self, path):
        self.root = path

    def get(self, path):
        self.render(self.root + path)
