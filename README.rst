*************
contentful.py
*************

|travis| |coveralls|

Python SDK for `Contentful`_'s Content Delivery API.

Setup
=====
Installation via ``pip``:

.. code-block:: bash

    pip install contentful-cda

Usage
=====

-----------------
Creating a Client
-----------------

The ``Client`` class manages all your interaction with the Contentful Delivery API, creating one is as simple as:

.. code-block:: python

    client = Client('space-id', 'access-token')

------------------
Fetching Resources
------------------

The simplest form of fetching resources follows:

.. code-block:: python

    client.fetch(Asset).all()         # Returns an array of Assets
    client.fetch(Asset).first()       # Returns the first Asset available

    client.fetch(Entry).all()         # Returns an array of Entries
    client.fetch(Entry).first()       # Returns the first Entry available

    client.fetch(ContentType).all()   # Returns an array of Content Types
    client.fetch(ContentType).first() # Returns the first Content Type available

When used with the ``all()`` method, expect an ``Array`` object to be returned, which is iterable:

.. code-block:: python

    for resource in array:
        dosomething(resource)

and sliceable:

.. code-block:: python

    for resource in array[2:4]:
        dosomething(resource)

--------------
Custom Queries
--------------

Custom queries can be provided by invoking the ``where()`` method of a ``Request`` object, for example:

.. code-block:: python

    client.fetch(Entry).where({'sys.id': 'MyEntry'}).first()

---------------
Defining Models
---------------

Custom Entry classes can be declared by providing a Content Type ID value and by defining a set of fields. Consider the ``Cat`` Content Type from the official demo space, which looks like this (sans some properties for brevity):

.. code-block:: json

    {
      "fields": [
        {"id": "name", "name": "Name", "type": "Text"},
        {"id": "likes", "name": "Likes", "type": "Array", "items": { "type": "Symbol" }},
        {"id": "color", "name": "Color", "type": "Symbol"},
        {"id": "bestFriend", "name": "Best Friend", "type": "Link", "linkType": "Entry"},
        {"id": "birthday", "name": "Birthday", "type": "Date"},
        {"id": "lives", "name": "Lives left", "type": "Integer"},
        {"id": "image", "name": "Image", "type": "Link", "linkType": "Asset"}
      ],
      "name": "Cat",
      "displayField": "name",
      "description": "Meow."
    }

A custom Entry class for this Content Type can be defined as follows:

.. code-block:: python

    class Cat(Entry):
        __content_type__ = 'cat'

        name = Field(Text)
        likes = Field(List)
        color = Field(Text)
        best_friend = Field(Link, field_id='bestFriend')
        birthday = Field(Date)
        lives = Field(Number)
        image = Field(Link)

The class also has to be registered when creating a ``Client``:

.. code-block:: python

    client = Client('cfexampleapi', 'b4c0n73n7fu1', custom_entries=[Cat])

Whenever this ``Client`` will attempt to create an ``Entry`` with a Content Type that matches the one defined in the class, an instance of the ``Cat`` class will be created, and it's fields will be set accordingly, and can later be easily accessed as instance attributes:

.. code-block:: python

    print('Name of the Cat: {0}'.format(cat.name))

If at any point it is desired to fetch only resources of that type, it can be passed to the ``fetch()`` method and inferred by the client:

.. code-block:: python

    client.fetch(Cat).all() # Fetches all the Cats!

---------------
Link Resolution
---------------

Unless specified otherwise, a ``Client`` is configured to resolve links automatically when fetching resources.
Be mindful about providing the ``include`` parameter properly, since only if the linked resources are contained within the response they will be resolved automatically. In case a link is not resolved, expect a ``ResourceLink`` value, which can be resolved by invoking the ``resolve_resource_link()`` method of a ``Client`` (issues a network request per the resource ID).

**Automatic link resolution:**

.. code-block:: python

    array = client.fetch(Cat).all()
    print(array[0].best_friend)
    # <Cat(sys.id=nyancat)>

**Manual link resolution:**

.. code-block:: python

    cat = client.fetch(Cat).where({'sys.id': 'nyancat', 'include': 0}).first()
    print(cat.best_friend)
    # <contentful.cda.resources.ResourceLink object at 0x1030df390>
    print(client.resolve_resource_link(cat.best_friend))
    # <Cat(sys.id=nyancat)>

License
=======

Copyright (c) 2015 Contentful GmbH. See `LICENSE.txt`_ for further details.


.. _Contentful: https://www.contentful.com
.. _LICENSE.txt: https://github.com/contentful/contentful.py/blob/master/LICENSE.txt

.. |travis| image:: https://travis-ci.org/contentful/contentful.py.svg
    :target: https://travis-ci.org/contentful/contentful.py/builds#
    
.. |coveralls| image:: https://img.shields.io/coveralls/contentful/contentful.py.svg
    :target: https://coveralls.io/r/contentful/contentful.py?branch=master
