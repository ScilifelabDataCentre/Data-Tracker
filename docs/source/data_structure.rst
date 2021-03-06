**************
Data Structure
**************

The Data Tracker is based on a few main components:

* Order
* Dataset
* Collection
* User
* Log


General
=======

* ``Title`` may never be empty.


Terminology
===========

* Fields:

  - Fields in the documents for the datatype/collection.

* Computed fields:

  - Values that are either calculated or retrieved from documents in other collection(s).
  - Included when the entity is requested via API.



Order
=====

* Requires special permission to add (``ORDERS_SPECIAL``)
* May only be accessed and modified by users listed in ``editors`` or users with ``DATA_MANAGEMENT``.
* Can have any number of associated datasets.
* Deleting an order will delete all owned datasets.

Summary
-------

+---------------+-----------------------------------------------------+-------------------+-----------------------+
| Field         | Description                                         | Default           | Public                |
+===============+=====================================================+===================+=======================+
| _id           | UUID of the Entry                                   | Set by system     | Hidden                |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| title         | Title of the Entry                                  | Must be non-empty | Hidden                |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| description   | Description in markdown                             | Empty             | Hidden                |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| generators    | List of users who generated data                    | Entry creator     | Visible (via dataset) |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| authors       | List of users responsible for e.g. samples (e.g PI) | Entry creator     | Visible (via dataset) |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| organisation  | User who is data controller                         | Entry creator     | Visible (via dataset) |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| editors       | List of users who can edit the order and datasets   | Entry creator     | Hidden                |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| receivers     | List of users who received data from facility       | Empty             | Hidden                |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| datasets      | List of associated datasets                         | Empty             | Visible (via dataset) |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| tags_standard | Tags defined in the system                          | Empty             | Hidden                |
+---------------+-----------------------------------------------------+-------------------+-----------------------+
| tags_user     | Tags defined by the users                           | Empty             | Hidden                |
+---------------+-----------------------------------------------------+-------------------+-----------------------+


Fields
------

:_id:
    * UUID of the entry.
    * Set by the system upon entry creation, never modified.
:title:
    * Entry title.
    * Must be non-empty.
:description:
    * Entry description.
    * May use markdown for formatting.
    * **Default:** Empty
:generators:
    * List of ``users``.

    * Corresponds to e.g. the facility or people generating the data (from samples).

    * May be shown openly on all associated datasets.

      - Access may be limited by other settings.

    * **Default:** The user that created the entry.
:authors:
    * List of ``users``.

    * Corresponds to e.g. the researcher who leads the project the samples came from.

    * May be shown openly on all associated datasets.

      - Access may be limited by other settings.

    * **Default:** The user that created the entry.
:organisation:
    * A single ``user`` who is the data controller for the datasets generated from the order (e.g. a University).
    * **Default:** The user that created the entry.
:editors:
    * List of ``users``.
    * Users that may edit the order and dataset entries. May add datasets to an order.
    * **Default:** The user that created the entry.
:receivers:
    * List of ``users``.
    * Corresponds to the users who received the data from the facility
    * **Default:** Empty
:datasets:
    * List of datasets associated to the order.
    * Cannot be modified directly but must be modified through specialised means.
    * **Default:** Empty
:tags_standard:
    * A standard set of tags that are defined by the system.
    * **Default:** Empty
:tags_user:
    * User-defined tags for the system.
    * **Default:** Empty


Dataset
=======

* Dataset generated by e.g. facility.
* A dataset must be associated with **one** order.
* Multiple datasets may be associated with the same order.

* The association to a specific order cannot be changed.

  -  Once associated with an order, it will stay so.

* Can have identifier(s) (e.g. DOIs).
* Will use some fields from its order:

  - ``generators``
  - ``authors``
  - ``organisation``
  - ``editors``
  - ``receivers``

Summary
-------

+------------------+----------------------------------+-------------------+---------+
| Field            | Description                      | Default           | Public  |
+==================+==================================+===================+=========+
| _id              | UUID of the Entry                | Set by system     | Visible |
+------------------+----------------------------------+-------------------+---------+
| title            | Title of the Entry               | Must be non-empty | Visible |
+------------------+----------------------------------+-------------------+---------+
| description      | Description in markdown          | Empty             | Visible |
+------------------+----------------------------------+-------------------+---------+
| tags_standard    | Tags defined in the system       | Empty             | Visible |
+------------------+----------------------------------+-------------------+---------+
| tags_user        | Tags defined by the users        | Empty             | Visible |
+------------------+----------------------------------+-------------------+---------+
| cross_references | External identifiers, links etc. | Empty             | Visible |
+------------------+----------------------------------+-------------------+---------+


Fields
------
:_id:
    * UUID of the entry.
    * Set by the system upon entry creation, never modified.
:title:
    * Entry title.
    * Must be non-empty.
:description:
    * Entry description.
    * May use markdown for formatting.
    * **Default:** Empty
:tags_standard:
    * A standard set of tags that are defined by the system.
    * **Default:** Empty
:tags_user:
    * User-defined tags for the system.
    * **Default:** Empty
:cross_references:
    * External references to the data.
    * E.g. DOIs or database IDs.
    * **Default:** Empty


Computed fields
---------------
:related:
    * ``datasets`` from order, except the current dataset.
:collections:
    * List of collections containing the current dataset in ``datasets``.
:generators:
    * ``generators`` from order.
:authors:
    * ``authors`` from order.
:organisation:
    * ``organisation`` from order.


Collection
==========

* May be created by any users.
* Can have multiple ``editors``.
* Can have identifiers.
* Provides a way of grouping datasets before publication.
* Should aid requesting a DOI from Figshare for the collection.


Summary
-------

+------------------+---------------------------------------------------+-------------------+---------+
| Field            | Description                                       | Default           | Public  |
+==================+===================================================+===================+=========+
| _id              | UUID of the Entry                                 | Set by system     | Visible |
+------------------+---------------------------------------------------+-------------------+---------+
| title            | Title of the Entry                                | Must be non-empty | Visible |
+------------------+---------------------------------------------------+-------------------+---------+
| datasets         | The associated datasets                           | Empty             | Visible |
+------------------+---------------------------------------------------+-------------------+---------+
| description      | Description in markdown                           | Empty             | Visible |
+------------------+---------------------------------------------------+-------------------+---------+
| tags_standard    | Tags defined in the system                        | Empty             | Visible |
+------------------+---------------------------------------------------+-------------------+---------+
| tags_user        | Tags defined by the users                         | Empty             | Visible |
+------------------+---------------------------------------------------+-------------------+---------+
| cross_references | External identifiers, links etc.                  | Empty             | Visible |
+------------------+---------------------------------------------------+-------------------+---------+
| editors          | List of users who can edit the collection         | Entry creator     | Hidden  |
+------------------+---------------------------------------------------+-------------------+---------+


Fields
------
:_id:
    * UUID of the collection.
    * Set by the system upon entry creation, never modified.
:title:
    * Entry title.
    * Must be non-empty.
:description:
    * Entry description.
    * May use markdown for formatting.
    * **Default:** Empty
:tags_standard:
    * A standard set of tags that are defined by the system.
    * **Default:** Empty
:tags_user:
    * User-defined tags for the system.
    * **Default:** Empty
:cross_references:
    * External references to the data.
    * E.g. DOIs or database IDs.
    * **Default:** Empty
:editors:
    * List of ``users``.
    * Users that may edit the collection.

      - May add datasets to an order.

    * **Default:** The user that created the entry.



User
====

* Everyone using the system is a user.

  - Including facilities, organisations ...

* Login via e.g. Elixir AAI or API key.

  - On first login, the user will be added to db.

* API can also be accessed using an API key.

  - API key may be generated by any user.

* A user with the permission ``USER_MANAGEMENT`` can create and modify users.
* A user with the permission ``ORDER_USERS`` can create and modify "partial" users.


Summary
-------

+--------------+-------------------------------------+-------------------+---------+
| Field        | Description                         | Default           | Public  |
+==============+=====================================+===================+=========+
| _id          | UUID of the Entry                   | Set by system     | Hidden  |
+--------------+-------------------------------------+-------------------+---------+
| affiliation  | User affiliation (e.g. university)  | Empty             | Visible |
+--------------+-------------------------------------+-------------------+---------+
| api_key      | Hash for the API key                | Empty             | Hidden  |
+--------------+-------------------------------------+-------------------+---------+
| api_salt     | Salt for API api_key                | Empty             | Hidden  |
+--------------+-------------------------------------+-------------------+---------+
| auth_ids     | List of identfiers from e.g. Elixir | Empty             | Hidden  |
+--------------+-------------------------------------+-------------------+---------+
| email        | Email address for the user          | Must be non-empty | Hidden  |
+--------------+-------------------------------------+-------------------+---------+
| email_public | Email address to show publicly      | Empty             | Visible |
+--------------+-------------------------------------+-------------------+---------+
| name         | Name of the user                    | Must be non-empty | Visible |
+--------------+-------------------------------------+-------------------+---------+
| orcid        | ORCID of the user                   | Empty             | Visible |
+--------------+-------------------------------------+-------------------+---------+
| permissions  | List of permissions for the user    | Empty             | Hidden  |
+--------------+-------------------------------------+-------------------+---------+
| url          | URL to e.g. homepage                | Empty             | Visible |
+--------------+-------------------------------------+-------------------+---------+


Fields
------

:_id:
    * UUID of the entry.
    * Set by the system upon entry creation, never modified.
:affiliation:
    * Affiliation of the user.
:api_key:
    * Hash for the API key for authorization to API or login.
:api_salt:
    * Salt for the API key.
:auth_ids:
    * List of identifiers used by e.g. Elixir AAI.
    * Saved as strings.
    * The general form is ``email@location.suffix::source``, but the style may vary between sources.
    * Any of the auth_id can be used with the API key.
:email:
    * Email address for the user.
    * **Default:** Must be set
:email_public:
    * Email to show to public on e.g. generated datasets.
    * **Default:** Empty.
:name:
    * Name of the user.

      - Could also be name of e.g. facility or university.
:orcid:
    * ORCID of the user.
:permissions:
    * A list of the extra permissions the user has (see :ref:`permissions_section`).
:url:
    * Url to e.g. a homepage
    * If set, it must start with ``http://`` or ``https://``.
    * **Default:** Empty



Log
===

* Whenever an entry (``order``, ``dataset``, ``collection``, or ``user``) is changed, a log should be written.
* Only visible to entry owners and admins.
* All logs are in the same collection.
* The log needs parsing to show changes between different versions of an entry.
* A full cope of the new entry is saved.

  - In case of deletion, ``_id`` is saved as ``data``.


Summary
-------

+-------------+--------------------------------------------+-------------------+
| Field       | Description                                | Default           |
+=============+============================================+===================+
| _id         | UUID of the Entry                          | Set by system     |
+-------------+--------------------------------------------+-------------------+
| action      | type of action                             | Must be non-empty |
+-------------+--------------------------------------------+-------------------+
| comment     | Short description of the action            | Empty             |
+-------------+--------------------------------------------+-------------------+
| data_type   | The modified collection (e.g. order)       | Must be non-empty |
+-------------+--------------------------------------------+-------------------+
| data        | Complete copy of the new entry             | Must be non-empty |
+-------------+--------------------------------------------+-------------------+
| timestamp   | Timestamp for the change                   | Must be non-empty |
+-------------+--------------------------------------------+-------------------+
| user        | UUID for the user who performed the action | Must be non-empty |
+-------------+--------------------------------------------+-------------------+


Fields
------

:_id:
    * UUID of the entry.
    * Set by the system upon entry creation, never modified.
:action:
    * Type of action

      - Add
      - Edit
      - Delete
:comment:
    * Short description of why it was made

      - "Add Dataset from order ``X``".
:data_type:
    * The collection that was modified, e.g. ``order``
:data:
    * Add/edit: full copy of the new/updated document.
    * Delete: the ``_id`` of the document.
:timestamp:
    * The time the action was performed.
:user:
    * ``_id`` of the user that performed the action.
    * Can be set to ``system`` for automated actions (e.g. creating a user after OIDC login)
