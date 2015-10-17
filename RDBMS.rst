Notes on implementing generatonal sets using RDBMSs
==================================================

It should be possible to use relational databases as well.

This document brainstorms how this might work.

.. contents::

Review: the basic object model
==============================

At the heart of the ZODB implementation are 3 mappings:

#. ``{generation -> object}``

#. ``{id -> generation}}``

#. Removals: ``{generation -> id}``

Note that we have both objects and ids.  We can't rely on objects
being useful keys, so we need to have separate object ids.  Also, in a
general, we may not be able to look up objects given an id, so we keep
a mapping from generation to object.

Leveraging an existing id object mapping.
------------------------------------------

If we had an id to object mapping, we could stop maintaining a
generation to object mapping.

If objects stored in relational databases had primary keys, we could
use these as the basis of generational sets.

Similarly, we could choose to leverage ZODB objects ids to do the same
thing.

An RDBMS approach
=================

Assume we want multiple generational sets, typically qualified by
something like a user id, or by type.  For different types, we might
define separate tables to model different sets.  For data-qualified
sets, we could use a single table with a colum to qualify data.

For example, let's suppose we want to model messages, such that users
can have multiple messages and messages can be sent to multiple users.

Assume we already have a `message`` table (and probably a ``user``
table), with a primary key, ``id``.

We create a ``user_message_generations`` table::

  create table user_message_generations (
    generation long auto_increment
    user_id foreign key references user(id)
    message_id foreign key references message(id)
    );

When we send a message, we store the message in the database and, for
each recipient, we::

  insert into user_message_generations (user_id, message_id)
         values ($recipient_id, message_id);

In our system, messages are mutable.  When we mutate a message, we
update the message record and then::

  delete from user_message_generations where message_id = $updated_id;

and for each recipient::

  insert into user_message_generations (user_id, message_id)
         values ($recipient_id, $message_id);

To get new and updated messages for a user::

  select message.* from message, user_message_generations
     where message.id = user_message_generations.message_id
           and
           user_message_generations.user_id = $given_user_id
           and
           generation > $given_generation

We also allow message retraction.  We need to be prepared to delete
messages users have already seen.  We use a separate table for this::

  create table user_message_generational_removals (
    generation long auto_increment
    user_id foreign key references user(id)
    message_id foreign key references message(id)
    );

When we retract a message, we remove it from
``user_message_generations`` and add it to
``user_message_generations_removals``::

  delete from user_message_generations where message_id = $updated_id;

and for each recipient::

  insert into user_message_generational_removals (user_id, message_id)
         values ($recipient_id, $message_id);

Now, when computing user updates, we also need to look for removals::

  select message_id from user_message_generations
     where user_message_generations.user_id = $given_user_id
           and
           generation > $given_generation

At this point, we can delete the message from the message table, at
least as long as we're sure the message id won't be reused.

If we don't mind keeping retracted message records around in the
user_message_generational_removals table, we're done.

If we want to clean up removal records, it gets complicated.  One
would be tempted to remove the removal records after we sent them to
the user, but the user might be using multiple clients. One could have
a rule that if a user's generation is > 0 and less than the minimum
removal generation and is there are at least as many removals as we're
willing to keep, then we can tell the user's client to discard all
messages and send them a complete set. This is what the ZODB
implementation does.  This would require an extra query to get the removal
count for a user.

Unqualified generational sets
-----------------------------

If we have generational sets that aren't qualified based on a user, we
can include the generation in the data records and avoid the extra
tables.  For example, suppose we have a task system. All users see all
tasks.  When we create or update a task, we can assign it a
generation, and retrieve from the task table without resorting to
joins.  We can use a remove flag on the task to keep track of removed
tasks and use that in the query.

Implementing generations
------------------------

The ideal way to implement generations is with sequences that can be
shared accross multiple tables.  This is necessary of you want to
track different kinds of data for a single generation, or even if you
want separate content and removal tables.

