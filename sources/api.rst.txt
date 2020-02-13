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


User
=======
.. function:: /user/me

    **GET** Get information about the current user


.. function:: /user/edit

    **GET** Update information of current user


.. function:: /user/edit/<uuid>

    **GET** Update information of user with uuid ``uuid``


.. function:: /user/logout

    **GET** Log out current user


.. function:: /user/login

    **GET** Log in user via elixir


.. function:: /user/all

    **GET** Get a list of all users


.. function:: /user/countries

    **GET** Get a list of countries


