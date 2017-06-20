Generational Sets
=================

Generational sets are designed to support a model of data
synchronization between clients.

Assumptions:

- Timeliness is important, but it's OK to display out-of-date data if
  disconnected.

- Connectivity is good enough to disallow local updates.

  This has the major advantage that there's no need to resolve
  conflicting updates made on disconnected clients.

  (A valid alternative would be to assume, for a given problem, that
  conflicts are so rare that failing hard on conflicts is acceptable,
  or, again for a given problem, to have changes that are, by their
  nature, non-conflicting.)

The approach is to have sets that have generations.

    >>> import zc.generationalset
    >>> set = zc.generationalset.GSet()
    >>> set.generation
    1

Note that ``GSet`` is just a shorthand:

    >>> zc.generationalset.GSet.__name__
    'GenerationalSet'

Items in a generational set must have ``id`` attributes (although the
attribute can have a different name)::

    >>> class Thing:
    ...     def __init__(self, id): self.id = id
    ...     def __repr__(self): return "Thing(%r)" % self.id
    >>> thing1 = Thing(1)

When items are added to a set, the set generation increases:

    >>> set.add(thing1)
    >>> set.generation
    2

Containment is based on ids:

    >>> thing1 in set
    True
    >>> Thing(1) in set
    True
    >>> Thing(2) in set
    False

You can also query containment using ids rather than objects.

    >>> 1 in set
    True
    >>> 2 in set
    False

As with regular sets, adding the same thing multiple times doesn't
affect the set size:

    >>> set.add(thing1)
    >>> len(set)
    1
    >>> list(set)
    [Thing(1)]

but it does increate the generation:

    >>> set.generation
    3

We can ask a set for generational_updates since a given generation:

    >>> from pprint import pprint
    >>> pprint(set.generational_updates(0))
    {'adds': [Thing(1)], 'generation': 3}
    >>> pprint(set.generational_updates(1))
    {'adds': [Thing(1)], 'generation': 3}
    >>> pprint(set.generational_updates(2))
    {'adds': [Thing(1)], 'generation': 3}
    >>> pprint(set.generational_updates(3))
    {'generation': 3}

The generational_updates can include additions or removals:

    >>> thing2 = Thing(2)
    >>> set.add(thing2)
    >>> set.remove(thing1)
    >>> pprint(set.generational_updates(3))
    {'adds': [Thing(2)], 'generation': 5, 'removals': [1]}

Note that a client can see a removal for an object it has never seen
an update for:

    >>> pprint(set.generational_updates(1))
    {'adds': [Thing(2)], 'generation': 5, 'removals': [1]}

But a client without data won't see removals:

    >>> pprint(set.generational_updates(0))
    {'adds': [Thing(2)], 'generation': 5}

A generational set keeps a limited number of removals generations.  This
is configurable:

    >>> set = zc.generationalset.GSet(maximum_removals=3)
    >>> for i in range(4):
    ...     set.add(Thing(i))
    ...     set.remove(Thing(i))

If we ask for a generation that would require a number of removals
greater than the maximum, the output won't contain generational_updates
or removals, signaling that the client should request the
entire set (for example by iterating over it).

    >>> pprint(set.generational_updates(0))
    {'generation': 9}
    >>> pprint(set.generational_updates(1))
    {'contents': [], 'generation': 9}
    >>> pprint(set.generational_updates(2))
    {'contents': [], 'generation': 9}
    >>> pprint(set.generational_updates(3))
    {'contents': [], 'generation': 9}
    >>> pprint(set.generational_updates(4))
    {'contents': [], 'generation': 9}
    >>> pprint(set.generational_updates(5))
    {'generation': 9, 'removals': [2, 3]}
    >>> pprint(set.generational_updates(6))
    {'generation': 9, 'removals': [2, 3]}
    >>> pprint(set.generational_updates(7))
    {'generation': 9, 'removals': [3]}
    >>> pprint(set.generational_updates(8))
    {'generation': 9, 'removals': [3]}
    >>> pprint(set.generational_updates(9))
    {'generation': 9}
    >>> pprint(set.generational_updates(10))
    {'generation': 9}

The removals that are lost are evicted from the internal data
structures.

    >>> len(set.removals)
    3
    >>> 0 in set.generations
    False

We can iterate over a set:

    >>> set = zc.generationalset.GSet()
    >>> for i in range(4):
    ...     set.add(Thing(i))

    >>> list(set)
    [Thing(0), Thing(1), Thing(2), Thing(3)]

We can ask for values from a generation:

    >>> list(set.values(4))
    [Thing(2), Thing(3)]

An object can only appear in one of adds and removals:

    >>> set = zc.generationalset.GSet(maximum_removals=3)
    >>> set.add(Thing(1))
    >>> from pprint import pprint
    >>> pprint(set.generational_updates(0))
    {'adds': [Thing(1)], 'generation': 2}

    >>> set.remove(Thing(1))
    >>> pprint(set.generational_updates(1))
    {'generation': 3, 'removals': [1]}

    >>> set.add(Thing(1))
    >>> pprint(set.generational_updates(0))
    {'adds': [Thing(1)], 'generation': 4}

    >>> set.remove(Thing(1))
    >>> pprint(set.generational_updates(1))
    {'generation': 5, 'removals': [1]}

Updating the Gset. Only if object is present in the set, it will be updated:

    >>> set = zc.generationalset.GSet()
    >>> set.add(Thing(1))
    >>> pprint(set.generational_updates(0))
    {'adds': [Thing(1)], 'generation': 2}


    >>> set.changed(Thing(2))
    Traceback (most recent call last):
    ...
    KeyError: 2

    >>> pprint(set.generational_updates(1))
    {'adds': [Thing(1)], 'generation': 2}

    >>> set.changed(Thing(1))
    >>> pprint(set.generational_updates(2))
    {'adds': [Thing(1)], 'generation': 3}

    >>> set.add(Thing(2))
    >>> pprint(set.generational_updates(3))
    {'adds': [Thing(2)], 'generation': 4}

    >>> set.changed(Thing(2))
    >>> pprint(set.generational_updates(4))
    {'adds': [Thing(2)], 'generation': 5}

    >>> pprint(set.generational_updates(0))
    {'adds': [Thing(1), Thing(2)], 'generation': 5}

Nested sets
-----------

You can define a nested set structure to form a tree.  In this
structure, all of the sets share a common generation and you can get
changes for for the entire tree in a single call. To use nested sets,
you pass in a parent set and an id when creating a set:

    >>> parent = zc.generationalset.GSet()
    >>> child1 = zc.generationalset.GSet('1', parent)
    >>> child2 = zc.generationalset.GSet('2', parent)

Note here that we didn't add child1 and child2 to parent.

    >>> len(parent)
    0

However, when we modify child1 and child, they'd add themselves to the parent:

    >>> child1.add(Thing('11'))
    >>> child1.add(Thing('12'))
    >>> child2.add(Thing('21'))
    >>> child2.add(Thing('22'))
    >>> child2.remove(Thing('22'))

    >>> len(parent)
    2

Now we can ask the parent for updates:

    >>> pprint(parent.generational_updates(2))
    {'adds': [{'adds': [Thing('12')], 'id': '1'},
              {'adds': [Thing('21')], 'id': '2', 'removals': ['22']}],
     'generation': 6}
    >>> pprint(parent.generational_updates(3)) # doctest: +NORMALIZE_WHITESPACE
    {'adds': [{'adds': [Thing('21')], 'id': '2', 'removals': ['22']}],
     'generation': 6}
    >>> pprint(parent.generational_updates(4))
    {'adds': [{'id': '2', 'removals': ['22']}], 'generation': 6}
    >>> pprint(parent.generational_updates(5))
    {'adds': [{'id': '2', 'removals': ['22']}], 'generation': 6}
    >>> pprint(parent.generational_updates(6))
    {'generation': 6}

Sets can be nested to arbitrary levels:

    >>> child11 = zc.generationalset.GSet('11', child1)
    >>> child12 = zc.generationalset.GSet('12', child1)

    >>> child111 = zc.generationalset.GSet('111')
    >>> child11.add(child111)
    >>> child112 = zc.generationalset.GSet('112')
    >>> child11.add(child112)

In these last 2 examples, we didn't set the parent. It was set when we
added the children to child11.

    >>> child111.parent is child11
    True

    >>> pprint(parent.generational_updates(6))
    {'adds': [{'adds': [{'adds': [{'id': '111'}, {'id': '112'}], 'id': '11'}],
               'id': '1'}],
     'generation': 8}

When a child is updated, it's generation because the same as the root object:

    >>> child111.add(Thing('1111'))
    >>> child111.generation == parent.generation
    True

    >>> pprint(parent.generational_updates(8))
    {'adds': [{'adds': [{'adds': [{'adds': [Thing('1111')], 'id': '111'}],
                         'id': '11'}],
               'id': '1'}],
     'generation': 9}

Notifications
-------------

When a top-level set's generation increases, it calls
``zc.generationalset.notify`` passing itself.  The ``notify`` function
doesn't do anything, but applications can replace it to do something
else (including replacing it with zope.event.notify).

    >>> import mock
    >>> with mock.patch('zc.generationalset.notify') as notify:
    ...     child2.add(Thing('23'))
    ...     notify.assert_called_once_with(parent)

Specifying object ids
---------------------

Normally, object ids come from item ``id`` attributes, but we can
supply ids explicitly:

    >>> set = zc.generationalset.GSet()
    >>> set.add((Thing(1), Thing(2)), (1, 2))
    >>> set.add((Thing(3), Thing(4)), (3, 4))
    >>> pprint(set.generational_updates(0))
    {'adds': [(Thing(1), Thing(2)), (Thing(3), Thing(4))], 'generation': 3}

    >>> (1, 2) in set
    True
    >>> (1, 3) in set
    False

Retrieving objects by their ids
-------------------------------

Objects can be retrieved by the object id:

    >>> ob = (Thing(1), Thing(2))
    >>> set.add(ob, (1,2))
    >>> set[(1,2)] == ob
    True

Attempting to retrieve a non-existing object results in a KeyError:

    >>> set[(42, 43)]
    Traceback (most recent call last):
      ...
    KeyError: (42, 43)

Using alternate ids
-------------------

By default, an ``id`` attribute is to get ids, but you can specify an
alternate id attribute:

    >>> class Other:
    ...    def __init__(self, **kw): self.__dict__.update(kw)
    ...    def __repr__(self): return "Other(%r)" % self.__dict__

    >>> set = zc.generationalset.GSet(id_attribute='name')
    >>> set.add(Other(name='foo'))
    >>> set.add(Other(name='bar'))
    >>> set.remove(Other(name='foo'))
    >>> pprint(set.generational_updates(1))
    {'adds': [Other({'name': 'bar'})], 'generation': 4, 'removals': ['foo']}

For more complicated situations, you can subclass ``GenerationalSet``
and override ```get_id(ob)``:

    >>> class StringIdGenerationalSet(zc.generationalset.GenerationalSet):
    ...     def get_id(self, ob):
    ...         return str(super(StringIdGenerationalSet, self).get_id(ob))

    >>> set = StringIdGenerationalSet()
    >>> set.add(Thing(1))
    >>> set.add(Thing(2))
    >>> set.remove(Thing(1))
    >>> pprint(set.generational_updates(1))
    {'adds': [Thing(2)], 'generation': 4, 'removals': ['1']}

Thanks to JavaScript, the need to convert integer ids to strings is
pretty common, so StringIdGenerationalSet is included:

    >>> zc.generationalset.SGSet.__name__
    'StringIdGenerationalSet'

    >>> set = zc.generationalset.SGSet()
    >>> set.add(Thing(1))
    >>> set.add(Thing(2))
    >>> set.remove(Thing(1))
    >>> pprint(set.generational_updates(1))
    {'adds': [Thing(2)], 'generation': 4, 'removals': ['1']}

There's also a flavor of generational set that uses items as their own ids:

    >>> zc.generationalset.VGSet.__name__
    'ValueGenerationalSet'
    >>> set = zc.generationalset.VGSet()
    >>> set.add((1, 2))
    >>> set.add((3, 4))
    >>> set.remove((1, 2))
    >>> pprint(set.generational_updates(1))
    {'adds': [(3, 4)], 'generation': 4, 'removals': [(1, 2)]}
