System Design
**************

Vision
======

It is very difficult to track the output and impact of the facilities at SciLifeLab. The Data Tracker is intended as an attempt to improve this by providing all generated data with unique identifiers that can be used to refer to the generated data.

The Data Tracker is designed based on the concept of three entities **orders**, **datasets**, and **collections**.

An **order** is simply an order to a facility. It may be a request for a microscope image, whole-genome sequencing of multiple samples, protein quantification, or any other service provided by a facility. Each **order** is expected to generate one or more **datasets**. Each dataset may refer to one or more analysed samples. All **datasets** generated from the same **order** are considered to be related. **Datasets** can be grouped together using **collections**, e.g. to show that orders from different facilities all are connected to the same research project.

**Orders** are intended to be private, while all information about **datasets** and **collections** is public.

All three entities will get one or more unique identifier, with the option of generating DOIs for specific datasets and collections.


Implementation
===============

The Data Tracker is implemented as a backend in Flask. All interactions with the system are intended to be done via the API, but a frontend (written in Quasar) is also available to simplify visualisation and usage.

The data structure is listed on the :ref:`data_structure` page. 

.. _permissions_section:


Permissions
-----------

* The permissions system is based on topics
* The topics are defined as key-value pairs
  * The value is the key and any other topics covered by the topic, e.g. ``DATA_MANAGEMENT`` also gives ``DATA_EDIT`` and ``USER_ADD``
* The topics are defined in ``user.py``

Current topics
^^^^^^^^^^^^^^

::

    {
      "DATA_EDIT": ("DATA_EDIT", "USER_ADD", "USER_SEARCH"),
      "OWNERS_READ": ("OWNERS_READ",),
      "USER_ADD": ("USER_ADD",),
      "USER_SEARCH": ("USER_SEARCH",),
      "USER_MANAGEMENT": ("USER_MANAGEMENT", "USER_ADD", "USER_SEARCH"),
      "DATA_MANAGEMENT": ("DATA_EDIT", "OWNERS_READ", "DATA_MANAGEMENT"),
     }

DATA_EDIT
    May create, edit, and delete orders, datasets, and collections if listed as an editor for the order.
DATA_MANAGEMENT
    May modify any order, dataset, or project.
OWNERS_READ
    May access all entity owner information.
USER_ADD
    May add users.
USER_SEARCH
    May list and search for users.
USER_MANAGEMENT
    May modify any user. Includes `USER_ADD` and `USER_SEARCH`.


Authorisation
-------------

Access is granted either via a session cookie or by including the users API key in the ``X-API-Key`` header. If a session is used, the value of the cookie ``_csrf_token`` must be included with the header ``X-CSRFToken`` for any non-``GET`` requests.

All cookies are deleted upon logout.


Testing
-------

All backend tests are available in the folder ``backend/tests``.
