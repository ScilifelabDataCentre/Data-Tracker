***
API
***

Base URL for the API is ``<url>/api``. All API description have the base implied before the first ``/``.

Order
=====

    .. note::

        Only for users with ``ORDERS_SELF`` or ``USER_MANAGEMENT``.


.. function:: /order/

    **GET** Get a list of all orders the user can access. All orders will be listed for a user with ``DATA_MANAGEMENT``.
    Can be limited by parameters.

    **POST** Add a new order.


.. function:: /order/<identifier>

    **GET** Get information about the order with uuid ``identifier``.

    **DELETE** Delete the order with uuid ``identifier``.

    **PATCH** Update the order with uuid ``identifier``.


.. function:: /order/<identifier>/dataset

    **POST** Add a new dataset belonging to order with uuid ``identifier``.


.. function:: /order/user/

    **GET** Get a list of orders created or received by current user.
    

.. function:: /order/<identifier>/log

    **GET** Get a list of changes done to the order with uuid ``identifier``.


Dataset
=======

.. function:: /dataset/

    **GET** Get a list of all datasets. Can be limited by parameters.


.. function:: /dataset/user/

    **GET** Get a list of datasets created or received by current user.


.. function:: /dataset/<identifier>/

    **GET** Get information about the dataset with uuid ``identifier``.

    **DELETE** Delete the dataset with uuid ``identifier``.

    **PATCH** Update the dataset with uuid ``identifier``.


.. function:: /dataset/<identifier>/log/

    **GET** Get a list of changes done to the dataset with uuid ``identifier``.


Project
=======

.. function:: /project/

    **GET** Get a list of all projects. Can be limited by parameters.

    **POST** Add a new project.


.. function:: /project/user/[username>/]

    **GET** Get a list of projects created or received by current user.


.. function:: /project/<identifier>/

    **GET** Get information about the project with uuid ``identifier``.

    **DELETE** Delete the project with uuid ``identifier``.

    **PATCH** Update the project with uuid ``identifier``.


.. function:: /project/<identifier>/log/

    **GET** Get a list of changes done to the project with uuid ``identifier``.


User
====

.. function:: /user/

    .. note::

        Only for users with ``USER_MANAGEMENT``.

    **GET** Get a list of all users.

    **POST** Add a new user.


.. function:: /user/me/

    **GET** Get information about the current user.

    **PUT** Update information about the current user.


.. function:: /user/me/apikey/

    **POST** Generate a new API key for the current user.


.. function:: /user/me/log/

    **GET** Get a list of changes done to the current user.


.. function:: /user/me/actions/

    **GET** Get a list of changes done by the current user.


.. function:: /user/<uuid>/

    .. note::

        Only for users with ``USER_MANAGEMENT``.


    **GET** Get information about user with ``uuid``.

    **PUT** Update information about user with ``uuid``.

    **PUT** Delete the user with ``uuid``.


.. function:: /user/<uuid>/apikey/

    .. note::

        Only for users with ``USER_MANAGEMENT``.


    **POST** Generate a new API key for the user with ``uuid``.


.. function:: /user/<uuid>/log/

    .. note::

        Only for the actual user and users with ``USER_MANAGEMENT``.

    **GET** Get a list of changes done to the user with ``uuid``.


.. function:: /user/<uuid>/actions/

    .. note::

        Only for the actual user and users with ``USER_MANAGEMENT``.

    **GET** Get a list of changes done by the user with ``uuid``.


.. function:: /user/logout/

    **GET** Log out current user.


.. function:: /user/login/oidc/

    **GET** Log in using OpenID Connect (e.g. Elixir AAI)


.. function:: /user/login/apikey/

    **GET** Log in using auth_id/api_key
