Configuration
*************

A sample configuration file is available with the name ``config.yaml.sample``. A sample setup can be seen in the ``docker-compose.yml`` file.

mongo.host
  Hostname for the database, e.g. ``localhost``.
mongo.port
  Port for the database, e.g. ``27017``.
mongo.user
  Username for the user, e.g. ``mongoadmin``.
mongo.password
  Password for the user, e.g. ``password``.
mongo.db
  The name of the database to use, e.g. ``data-tracker``.
flask.secret
  The key used to sign e.g. session cookies, e.g. ``ijltvEY9lSRu4E4moHfguY-r41ORr6kd``.
dev_mode.api
  Whether the ``/development`` part of the API should be activated, enabling e.g. password-less logins. It is required to run the backend tests.
dev_mode.testing
  Whether the ``development`` environment for the backend should be activated, including e.g. debugger and automatic code reloads.
oidc
  Lists the OpenID Connect entries. The key used will be the text on the log in button in the frontend.
oidc.<entry>.client_secret
  The client secret of the OpenID Connect entry
oidc.<entry>.client_id
  The client id of the OpenID Connect entry
oidc.<entry>.server_metadata_url
  The url for the configuration of the OpenID Connect entry
