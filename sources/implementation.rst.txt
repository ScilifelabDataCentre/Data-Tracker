Implementation
**************

.. _permissions_section:

Permissions
===========

* Permissions are managed by topics.
* A user may have multiple topics.
* The topics are defined in ``user.py``.
* The topics are defined as a dict::

    {
      'ENTRY': ('ENTRY', 'ENTRY2'),
      ...
    }

* Each topic is defined as key, and any other topics that are considered to cover the same task is included as value.
  - Allows the use a single topic to require permission for an API endpoint.
* ``permission_required`` is used to check whether a user has the required permission.
  - It is not defined as a decorator, as it may sometimes need to coexist with an ownership check.
  - At the beginning of a request, run e.g. ``user.permission_required('OWNERS_READ')``.


Current units
-------------

LOGGED_IN
    Task require a logged in user (e.g. show user info). Use the decorator ``user.login_required``.
DATA_MANAGEMENT
    May modify any order, dataset, or project. Includes ``ORDERS`` and ``OWNERS_READ``.
ORDERS
    May create, edit, and delete orders if listed as an editor for the order. Includes `USER_ADD` and `USER_SEARCH`.
OWNERS_READ
    May access all entity owner information.
USER_ADD
    May add users.
USER_SEARCH
    May list and search for users.
USER_MANAGEMENT
    May modify any user. Includes `USER_ADD` and `USER_SEARCH`.


CSRF
====

A csrf cookie with the name ``_csrf_token`` is set the first time a request is made to the system. It must be included with the header ``X-CSRFToken`` for any non-``GET`` request.

All cookies are deleted upon logout.


Testing
=======

All tests are available at ``backend/tests``.


API Keys
========

The keys are generated using ``secrets.token_hex(48)``.

Include a 8-byte randomized salt when calculating hash.

Store the token using ``hashlib.sha512(token).hexdigest()``.
