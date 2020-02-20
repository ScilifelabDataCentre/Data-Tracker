***
API
***

Base URL for the API is ``<url>/api``. All API description have the base implied before the first ``/``.

Order
=====

.. function:: /order/<identifier>

    **GET** Get information about the order with uuid ``identifier``.

    **DELETE** Delete the order with uuid ``identifier``.

    **PUT** Update the order with uuid ``identifier``.


.. function:: /order/add

    **GET** Get an object describing the input fields for **POST**.

    **POST** Add a new order.


.. function:: /order/<identifier>/addDataset

    **GET** Get an object describing the input fields for **POST**.

    **POST** Add a new dataset belonging to order with uuid ``identifier``.


.. function:: /order/user

    **GET** Get a list of orders created or received by current user or ``username`` (if provided as parameter).
    

.. function:: /order/<identifier>/log

    **GET** Get a list of changes done to the order with uuid ``identifier``.


Dataset
=======

.. function:: /dataset/<identifier>

    **GET** Get information about the dataset with uuid ``identifier``.

    **DELETE** Delete the dataset with uuid ``identifier``.

    **PUT** Update the dataset with uuid ``identifier``.


.. function:: /dataset/all

    **GET** Get a list of all datasets. Can be limited by parameters.


.. function:: /dataset/user

    **GET** Get a list of datasets created or received by current user or ``username`` (if provided as parameter).


.. function:: /dataset/<identifier>/log

    **GET** Get a list of changes done to the dataset with uuid ``identifier``.


Project
=======
.. function:: /project/<identifier>

    **GET** Get information about the project with uuid ``identifier``.

    **DELETE** Delete the project with uuid ``identifier``.

    **PUT** Update the project with uuid ``identifier``.


.. function:: /project/all

    **GET** Get a list of all projects. Can be limited by parameters.


.. function:: /project/user

    **GET** Get a list of projects created or received by current user or ``username`` (if provided as parameter).


.. function:: /order/<identifier>/log

    **GET** Get a list of changes done to the project with uuid ``identifier``.


User
====
.. function:: /user/me

    **GET** Get information about the current user.

    **PUT** Update information about the current user.


.. function:: /user/me/claim

    **POST** Claim datasets (``email``->``UUID``) belonging to the current user.


.. function:: /user/me/log

    **GET** Get a list of changes done to the current user.


.. function:: /user/me/actionLog

    **GET** Get a list of changes done by the current user.


.. function:: /user/<uuid>

    **GET** Get information about user with ``uuid``.

    **PUT** Update information about user with ``uuid``.


.. function:: /user/<uuid>/log

    **GET** Get a list of changes done to the user with ``uuid``.


.. function:: /user/<uuid>/actionLog

    **GET** Get a list of changes done by the user with ``uuid``.


.. function:: /user/logout

    **GET** Log out current user.


.. function:: /user/login

    **GET** Log in via elixir.


.. function:: /user/all

    **GET** Get a list of all users.


.. function:: /user/countries

    **GET** Get a list of countries.


DOI
===
.. function:: /doi/<identifier>

    **GET** Get information about the entity with DOI ``identifier``.


.. function:: /doi/add

    **GET** Get expected data structure for adding a new doi.

    **POST** Add a new DOI.


.. function:: /doi/all

    **GET** Get a list of all DOIs.


.. function:: /doi/request/<identifier>

    **GET** Get information about the DOI request with uuid ``identifier``.

    **PUT** Update information about the DOI request with uuid ``identifier``.


.. function:: /doi/request/add

    **GET** Add a new DOI request.


.. function:: /doi/request/all

    **GET** Get a list of all DOI requests.


.. function:: /doi/request/open

    **GET** Get a list of all open DOI requests.
