***********
Permissions
***********

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
=============

LOGGED_IN
    Task require a logged in user (e.g. show user info)
ORDERS_SELF
    CRUD permissions for owned orders and datasets for the orders.
DATA_MANAGEMENT
    May modify any order, dataset, or project. Includes ``ORDERS_SELF`` and ``OWNERS_READ``.
OWNERS_READ
    May access all entity owner information.
USER_MANAGEMENT
    May modify any user.
DOI_REVIEWER
    May evaluate and accept DOI requests.
