contentful.py
=============

[![Build Status](https://magnum.travis-ci.com/contentful/contentful.py.svg?token=J8uWM5wmFQZTgYu2HNmp&branch=master)](https://magnum.travis-ci.com/contentful/contentful.py) [![Coverage Status](https://coveralls.io/repos/contentful/contentful.py/badge.png?branch=master)](https://coveralls.io/r/contentful/contentful.py?branch=master)

Python SDK for [Contentful's][1] Content Delivery API.

[Contentful][1] is a content management platform for web applications, mobile apps and connected devices. It allows you to create, edit & manage content in the cloud and publish it anywhere via powerful API. Contentful offers tools for managing editorial teams and enabling cooperation between organizations.

Setup
=====

Installation via pip:

```bash
pip install contentful-cda
```

Usage
=====

### Creating a Client

The `Client` class manages all your interaction with the Contentful Delivery API, creating one is as simple as:
```python
client = Client('space-id', 'access-token')
```

### Fetching Resources

The simplest form of fetching resources follows:

```python
client.fetch(Asset).all()         # Returns an array of Assets
client.fetch(Asset).first()       # Returns the first Asset available

client.fetch(Entry).all()         # Returns an array of Entries
client.fetch(Entry).first()       # Returns the first Entry available

client.fetch(ContentType).all()   # Returns an array of Content Types
client.fetch(ContentType).first() # Returns the first Content Type available
```

When used with the `all()` method, expect an `Array` object to be returned, which is iterable:

```python
for resource in array:
  dosomething(resource)
```

and sliceable:

```python
for resource in array[2:4]:
  dosomething(resource)
```

#### Providing a custom query:

Custom queries can be provided by invoking the `where()` method of a `Request` object, for example:

```python
client.fetch(Entry).where({'sys.id': 'MyEntry'}).first()
```

### Custom Entry Models

Custom Entry classes can be declared by providing a Content Type ID value and by defining a set of fields. Consider the `Cat` Content Type from the official demo space, which looks like this (sans some properties for brevity):

```json
{
  "fields": [
    {"id": "name", "name": "Name", "type": "Text"},
    {"id": "likes", "name": "Likes", "type": "Array", "items": { "type": "Symbol" } },
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
```

A custom Entry class for this Content Type can be defined as follows:

```python
class Cat(Entry):
    __content_type__ = 'cat'

    name = Field(Text)
    likes = Field(List)
    color = Field(Text)
    best_friend = Field(Link, field_id='bestFriend')
    birthday = Field(Date)
    lives = Field(Number)
    image = Field(Link)
```

The class also has to be registered when creating a `Client`:

```python
client = Client('cfexampleapi', 'b4c0n73n7fu1', custom_entries=[Cat])
```

Whenever this `Client` will attempt to create an `Entry` with a Content Type that matches the one defined in the class, an instance of the `Cat` class will be created, and the fields will be set accordingly, and can later be easily accessed as instance attributes:

```python
print 'Name of the Cat: {0}'.format(cat.name)
```

If at any point it is desired to fetch only resources of that type, it can be passed to the `fetch()` method and inferred by the client:

```python
client.fetch(Cat).all() # Fetches all the Cats!
```

### Link Resolution

All `Entry` instances have a `raw_fields` attribute, containing the *unmodified* values of the Entry as received from the API. In addition, there is the `fields` attribute, which contains all the original fields along with some modifications, a notable one would be that all links are replaced with `LinkedResource` objects instead of just dictionaries.

It is possible to resolve `LinkedResource` links by invoking one of the relevant methods in the `Client` class. All these methods take an optional `array` argument, if the linked resource is contained within the array items (or included items) it will be resolved immediately, otherwise a network request will be made.

One could resolve all links contained within an array by invoking the `resolve_array_links()` method of the `Client` class, for example:

```python
array = client.fetch(Entry).all()
client.resolve_array_links(array)
```

License
=======

Copyright (c) 2015 Contentful GmbH. See [LICENSE.txt][2] for further details.


 [1]: https://www.contentful.com
 [2]: LICENSE.txt
