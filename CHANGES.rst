Changes
*******

0.4.0 (2017-06-20)
==================

- Python 3 support

- When asking for updates from generation 0, only adds are sent. Never
  removals, making this common case more efficient.

0.3.0 (2014-08-28)
==================

- Added a ``changed`` method to make intent clear when simply recording changes.

- Fixed: exceptions were raised when objects added to generational
  sets quacked a little like generational sets.

0.2.0 (2014-08-10)
==================

- Improved subset APIs:

  - No longer need to specify superset flag.

  - Can have set and non-set children.

  - A subset can be created without a parent and the parent will be
    set when it's added to a containing set.

0.1.2 (2014-06-09)
==================

Fixed: Internal data structures were misshandled when there were more
       than the maximum number of removals.

(Release 0.1.1 was made in error.)

0.1.0 (2014-06-08)
==================

Initial release
