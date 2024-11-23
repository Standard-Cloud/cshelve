Writeback parameter
===================

The `writeback` argument in `cshelve` controls how modifications to objects stored in the database are persisted.
By default, `writeback` is set to `False`, meaning only explicit updates to the database are written back.
When `writeback` is enabled, changes to mutable objects are cached in memory and persisted upon synchronization or closure.

Default Behavior (`writeback=False`)
####################################

When `writeback` is `False`, changes to mutable objects retrieved from the database are **not** automatically saved. Only explicit writes persist updates to the database:

.. code-block:: python

   with cshelve.open('provider.ini', writeback=False) as db:
      db['numbers'] = [1, 2, 3]
      numbers = db['numbers']
      numbers.append(4)  # Changes the in-memory object only

      print(db['numbers'])  # [1, 2, 3]

      # To persist changes, the updated object must be reassigned:
      db['numbers'] = numbers


Enabling `writeback=True`
#########################

When `writeback` is set to `True`, `cshelve` caches all retrieved objects in memory.
Modifications to these objects are saved back to the database when `sync()` is called or when the database is closed:

.. code-block:: python

   with cshelve.open('provider.ini', writeback=True) as db:
      db['numbers'] = [1, 2, 3]
      numbers = db['numbers']
      numbers.append(4)  # Changes the cached object

      print(db['numbers'])  # [1, 2, 3, 4]

Changes remain in the local cache until explicitly synchronized.
To persist changes, call the `sync()` method or close the database:

.. code-block:: python

   with cshelve.open('provider.ini', writeback=True) as db:
      db['numbers'] = [1, 2, 3]
      numbers = db['numbers']
      numbers.append(4)

      db.sync()  # Changes are persisted to the database

   with cshelve.open('other-provider.ini', writeback=True) as db:
      db['numbers'] = [1, 2, 3]
      numbers = sdbtore['numbers']
      numbers.append(4)

   # Changes are persisted to the database when exiting the context manager


Trade-Offs of `writeback`
#########################

Benefits
--------

- Simplifies handling of mutable objects, as local changes are automatically tracked and persisted.
- Reduces the need for explicit reassignment of modified objects.
- Better performance until synchronization is required.

Drawbacks
---------

- Cached objects remain in memory until explicitly synchronized or the database is closed increasing the memory usage.
- Other consumers of the database cannot see updates until synchronization occurs.
- Data are not persisted immediately, which may lead to data loss if the application crashes before synchronization.
