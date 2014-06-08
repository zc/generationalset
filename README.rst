Generational Sets
*****************

Generational sets (GSets) are designed to facilitate data synchronization
between a server and clients.

Goals:

- Make synchronization simple by sending all updates for a tree of sets
  at once.

- Allow clients to be updated very quickly.

- Reduce data-transfer volume by sending only changes.

- Avoid conflict resolution.

Assumptions:

- Disconnected data updates aren't needed.

- Clients mirror server data.

  This implies that the server data, or more specifically, the user's
  view of the server data, aren't too large to store on the client.

GSets track state by generation.  A client presents a generation and
is sent updates made since the presented generation.  GSets can be
grouped into trees with a shared generation.  A client can present a
single generation and be send updates for all of the sets making up a
database.

This implementation of generational sets uses `ZODB
<http://zodb.org>`_ to store data on the server.

High-level usage pattern
========================

- Define a tree of sets representing the data in an application.
  This may be user specific.

- Clients make updates via REST calls to a server.  They don't make
  local changes except in response to server updates.

- Client requests include their data generation.

- Most (JSON) responses to server calls have optional updates property
  that contains generational updates since the generation provided by
  the client.  When the client gets updates, which include the new
  generation, it applies the updates to it's internal data store.

- For native apps, the server sends push notifications when there are
  updates for a user and, in response, the client polls for the
  updates.  This allows updates to be extremely timely without
  constant polling.

Note that this package only provides the data structure
implementation. Wrapping the data structure in a REST interface or
sending notifications is up to applications.

API
===

Every object in a GSet must have an id.  By default, this is provided
by an ``id`` attribute, but you can configure a GSet to use another
attribute or some other mechanism to get an id for an object.

When an object is added to a GSet, or when it changes, call the
``add`` method on the Gset with the object::

    >>> from zc.generationalset import GSet
    >>> things = GSet()
    >>> athing = Thing(42)
    >>> things.add(athing)

To remove an object, call
the ``remove`` method with the object::

    >>> things.remove(athing)

To get updates to a set since a given generation, call
``generational_updates``, passing a generation::

    >>> things.generational_updates(0)
    {'generation': 3, 'removals': [42]}

    >>> things.add(Thing(1))
    >>> things.generational_updates(0)
    {'generation': 4, 'removals': [42], 'adds': [Thing(1)]}
    >>> things.generational_updates(3)
    {'generation': 4, 'adds': [Thing(1)]}

Note that generations start at 1.

The result of calling ``generational_updates`` is a dictionary with
keys:

generation
  The current generation of the set

adds
  Objects added since the given generation.

removals
  Ids of objects removed since the given generation.

contents
  All of the object in the set.

  ``contents`` are returned when there have been many removals since
  the given generation.  A generational set only keeps track of a
  limited number (99 by default, but configurable) of removals.  If a
  client is too out of date for the set to have relevant removals, it
  returns the entire contents, instead of returning adds and removals.

GSets support iteration, and querying length and containment. They
don't currently support set operations, like intersection and
union. You can also retrieve an item from a GSet using it's id::

    >>> len(things)
    1
    >>> list(things)
    [Thing(1)]
    >>> Thing(1) in things
    True
    >>> things[1]
    Thing(1)

Nested sets
-----------

To define nested sets:

- Define a parent set::

    >>> parent = GSet(superset=True)

  Note the use of the ``superset`` parameter.

- Define child sets, and add them to the parent:

    >>> messages = GSet("messages", parent)
    >>> parent.add(messages)

  When defining child sets, specify an id and the parent.

We haven't tested more than one level of nesting.

When asking for generational updates on parent sets, the adds and
contents contain the generational updates for subsets, with ids, but
without subset generations:

    >>> messages.add(Thing(42))
    >>> parent.generational_updates(0)
    {'generation': 3, 'adds': [{'id': 'messages', 'adds': [Thing(42)]}]}

Changes
*******

0.1.0 (2014-06-08)
==================

Initial release
