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


.. function:: /order/

    **GET**
       * Get a list of all orders where the user is ``editor``.
       * All orders will be listed for a user with ``DATA_MANAGEMENT``.

    **PUT**
       * Add a new order.
       * Returns the ``uuid`` of the added order.


.. function:: /order/<uuid>/

    **GET**
       * Get information about the order ``uuid``.

    **DELETE**
       * Delete the order ``uuid``.

    **PATCH**
       * Update the order ``uuid``.


.. function:: /order/<uuid>/dataset/

    **PUT**
       * Add a new dataset for the order ``uuid``.
       * Returns the ``uuid`` of the added dataset.
    

.. function:: /order/<uuid>/log/

    **GET**
       * Get a list of changes for the order ``uuid``.


Dataset
=======

.. function:: /dataset/

    **GET**
       * Get a list of all datasets.


.. function:: /dataset/<uuid>/

    **GET**
       * Get information about the dataset ``uuid``.

    **DELETE**
       * Delete the dataset ``uuid``.

    **PATCH**
       * Update the dataset ``uuid``.


.. function:: /dataset/<uuid>/log/

    **GET**
       * Get a list of changes done to the dataset ``uuid``.


Collection
==========

.. function:: /collection/

    **GET**
       * Get a list of all collections.

    **PUT**
       * Add a new collection.


.. function:: /collection/<uuid>/

    **GET**
       * Get information about the collection ``uuid``.

    **DELETE**
       * Delete the collection ``uuid``.

    **PATCH**
       * Update the collection ``uuid``.


.. function:: /collection/<uuid>/log/

    **GET**
       * Get a list of changes done to the collection ``uuid``.


User
====

Current User
------------

.. function:: /user/me/

    **GET**
       * Get information about the current user.

    **PATCH**
       * Update information for the current user.


.. function:: /user/me/apikey/

    **POST**
       * Generate a new API key for the current user.
       * The new API key is returned.


.. function:: /user/me/log/

    **GET**
       * Get a list of changes done to the current user.


.. function:: /user/me/actions/

    **GET**
       * Get a list of changes done by the current user.


.. function:: /user/me/orders/

    **GET**
       * Get a list of orders where the current user is listed as ``editor``.
    

.. function:: /user/me/datasets/

    **GET**
       * Get a list of datasets where the current user is listed as ``editor``. 


.. function:: /user/me/collections/

    **GET**
       * Get a list of collections where the current user is listed as ``editor``. 


Look Up Users
-------------

.. note::

    Only for users with ``USER_MANAGEMENT``, or in some cases ``USER_SEARCH``.



.. function:: /user/

    .. note::

        Only for users with ``USER_SEARCH`` or ``USER_MANAGEMENT``.

    **GET**
       * Get a list of all users.
       * Users with ``USER_SEARCH`` will get a limited set of fields.

    **PUT**
       * Add a new user.


.. function:: /user/<uuid>/

    **GET**
       * Get information about the user ``uuid``.

    **PATCH**
       * Update information about the user ``uuid``.

    **DELETE**
       * Delete the user ``uuid``.


.. function:: /user/<uuid>/apikey/

    **POST**
       * Generate a new API key for the user ``uuid``.
       * The new API key is returned.


.. function:: /user/<uuid>/log/

    **GET**
       * Get a list of changes done to the user ``uuid``.


.. function:: /user/<uuid>/actions/

    **GET**
       * Get a list of changes done by the user with ``uuid``.


.. function:: /user/<uuid>/orders/

    **GET**
       * Get a list of orders where the user ``uuid`` is listed as ``editor``.
    

.. function:: /user/<uuid>/datasets/

    **GET**
       * Get a list of datasets where the user ``uuid`` is listed as ``editor``. 


.. function:: /user/<uuid>/collections/

    **GET**
       * Get a list of collections where the user ``uuid`` is listed as ``editor``. 


Log In/Log Out
--------------
    
.. function:: /logout/

    **GET**
       * Log out the current user.


.. function:: /login/oidc/<auth_name>/login/

    **GET**
       * Log in using OpenID Connect (e.g. Elixir AAI) for service ``auth_name``.


.. function:: /login/oidc/<auth_name>/authorize/

    **GET**
       * Authorize using OpenID Connect (e.g. Elixir AAI) for service ``auth_name`` (via ``login``).


.. function:: /login/apikey/

    **GET**
       * Log in using ``auth_id`` + ``api_key``.
