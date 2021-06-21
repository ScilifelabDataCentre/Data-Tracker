***
API
***

=========
Version 1
=========

Base URL for the API is ``<url>/api/v1/``. All API description have the base implied before the first ``/``.

Order
=====

.. note::

     Only for users with ``ORDERS`` or ``DATA_MANAGEMENT``.


.. function:: /order

    **GET**
       * Get a list of all orders where the user is ``editor``.
       * All orders will be listed for a user with ``DATA_MANAGEMENT``.

    **POST**
       * Add a new order.
       * Returns the ``uuid`` of the added order.

       ::

          {
            "order": {
              "title": "New title",
              "description": "Text as **Markdown**",
              "authors": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
              "generators": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
              "organisation": "271206a2-86e7-406a-b881-6b3abc94fd2f",
              "editors": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
              "tags": ["Tag"],
              "properties": {"Key": "Value"},
            }
          }


.. function:: /order/<uuid>

    **GET**
       * Get information about the order ``uuid``.

    **DELETE**
       * Delete the order ``uuid``.

    **PATCH**
       * Update the order ``uuid``.

       ::

          {
            "order": {
              "title": "New title",
              "description": "Text as **Markdown**",
              "authors": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
              "generators": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
              "organisation": "271206a2-86e7-406a-b881-6b3abc94fd2f",
              "editors": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
              "tags": ["Tag"],
              "properties": {"Key": "Value"},
            }
          }


.. function:: /order/<uuid>/dataset

    **POST**
       * Add a new dataset for the order ``uuid``.
       * Returns the ``uuid`` of the added dataset.

       ::

          {
            "dataset": {
              "title": "New title",
              "description": "Text as **Markdown**",
              "tags": ["Tag"],
              "properties": {"Key": "Value"},
            }
          }
    

.. function:: /order/<uuid>/log

    **GET**
       * Get a list of changes for the order ``uuid``.


Dataset
=======

.. function:: /dataset

    **GET**
       * Get a list of all datasets.


.. function:: /dataset/<uuid>

    **GET**
       * Get information about the dataset ``uuid``.

    **DELETE**
       * Delete the dataset ``uuid``.

    **PATCH**
       * Update the dataset ``uuid``.

       ::

          {
            "dataset": {
              "title": "New title",
              "description": "Text as **Markdown**",
              "tags": ["Tag"],
              "properties": {"Key": "Value"},
            }
          }


.. function:: /dataset/<uuid>/log

    **GET**
       * Get a list of changes done to the dataset ``uuid``.


Collection
==========

.. function:: /collection

    **GET**
       * Get a list of all collections.

    **POST**
       * Add a new collection.

       ::

          {
            "collection": {
              "title": "New title",
              "description": "Text as **Markdown**",
              "tags": ["Tag"],
              "properties": {"Key": "Value"},
              "editors": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
            }
          }


.. function:: /collection/<uuid>

    **GET**
       * Get information about the collection ``uuid``.

    **DELETE**
       * Delete the collection ``uuid``.

    **PATCH**
       * Update the collection ``uuid``.

       ::

          {
            "collection": {
              "title": "New title",
              "description": "Text as **Markdown**",
              "tags": ["Tag"],
              "properties": {"Key": "Value"},
              "editors": ["271206a2-86e7-406a-b881-6b3abc94fd2f"],
            }
          }


.. function:: /collection/<uuid>/log

    **GET**
       * Get a list of changes done to the collection ``uuid``.


User
====

Current User
------------

.. function:: /user/me

    **GET**
       * Get information about the current user.

    **PATCH**
       * Update information for the current user.

       ::

          {
            "user: {
              "affiliation": "University A",
              "name": "First Last",
              "orcid": "1111-1111-1111-1115",
              "contact": "Street 1, 234 56 City",
              "url": "https://www.example.com",
            }
          }


Look Up Users
-------------

.. note::

    Only for users with ``USER_MANAGEMENT``, or in some cases ``USER_SEARCH``.



.. function:: /user

    .. note::

        Only for users with ``USER_SEARCH`` or ``USER_MANAGEMENT``.

    **GET**
       * Get a list of all users.
       * Users with ``USER_SEARCH`` will get a limited set of fields.

    **POST**
       * Add a new user.

       ::

          {
            "user: {
              "affiliation": "University A",
              "name": "First Last",
              "orcid": "1111-1111-1111-1115",
              "contact": "Street 1, 234 56 City",
              "url": "https://www.example.com",
              "email": "name@example.com",
            }
          }


.. function:: /user/<uuid>

    **GET**
       * Get information about the user ``uuid``.

    **PATCH**
       * Update information about the user ``uuid``.


       ::

          {
            "user: {
              "affiliation": "University A",
              "name": "First Last",
              "orcid": "1111-1111-1111-1115",
              "contact": "Street 1, 234 56 City",
              "url": "https://www.example.com",
              "email": "name@example.com",
            }
          }


    **DELETE**
       * Delete the user ``uuid``.


.. function:: /user/<uuid>/apikey

    **POST**
       * Generate a new API key for the user ``uuid``.
       * The new API key is returned.


.. function:: /user/<uuid>/log

    **GET**
       * Get a list of changes done to the user ``uuid``.


.. function:: /user/<uuid>/actions

    **GET**
       * Get a list of changes done by the user with ``uuid``.


Log In/Log Out
--------------
    
.. function:: /logout

    **GET**
       * Log out the current user.


.. function:: /login/oidc/<auth_name>

    **GET**
       * Log in using OpenID Connect (e.g. Elixir AAI) for service ``auth_name``.


.. function:: /login/oidc/<auth_name>/authorize

    **GET**
       * Authorize using OpenID Connect (e.g. Elixir AAI) for service ``auth_name`` (via ``login``).


.. function:: /login/apikey

    **GET**
       * Log in using ``auth_id`` + ``api_key``.
