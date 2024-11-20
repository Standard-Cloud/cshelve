Tutorial: Getting Started with *cshelve*
========================================

Because the *cshelve* follows the *shelve* interface, a good getting started of the *cshelve* is the *shelve* `tutorial <https://docs.python.org/3/library/shelve.html>`_.

Installation
############

Before getting started, ensure that *cshelve* is installed:

.. code-block:: console

    $ pip install cshelve

Note that the default installation only includes the ``in-memory`` provider, which is suitable for testing and development but not recommended for production use. To use a specific provider, install the corresponding provider. For example, to use the ``azure-blob`` provider:

.. code-block:: console

    $ pip install cshelve[azure-blob]


Basic Usage
###########

The following examples demonstrate how to open a *cshelve* storage, save data, and retrieve it.

How to open a database
++++++++++++++++++++++

To start using *cshelve*, we need to open a database connection. The term "database" is used loosely here; it could be a local file, a cloud storage service, or an in-memory store.

.. code-block:: python

    import cshelve

    # Using a context manager
    with cshelve.open('config.ini') as db:
        ...

    # Or without a context manager but remember to close the database
    db = cshelve.open('config.ini')
    ...
    db.close()

Storing Data
++++++++++++

*cshelve* can store almost any Python object, including complex data types like lists, dictionaries, and custom objects. For example:

.. code-block:: python

    with cshelve.open('config.ini') as db:
        db['user_info'] = {'name': 'Alice', 'age': 28, 'location': 'New York'}
        db['friends'] = ['Bob', 'Carol', 'Dave']


These objects are automatically serialized and saved on the targeted provider.

Note: By nature, the ``in-memory`` provider does not persist data across program execution, but can between sessions.

Retrieving Data
+++++++++++++++

To retrieve data, simply access it by its key:

.. code-block:: python

    with cshelve.open('config.ini') as db:
        username = db['username']
        preferences = db['preferences']

        print(username)       # Output: Alice
        print(preferences)    # Output: {'theme': 'dark', 'notifications': True}

Just like with dictionaries, accessing a key that doesn't exist, *cshelve* will raise a ``KeyError``.

Updating Data
+++++++++++++

Updating data is as simple as assigning a new value to an existing key:

.. code-block:: python

    with cshelve.open('config.ini') as db:
        db['age'] = 42
        assert db['age'] == 42

        # Update an existing key
        db['age'] = 21
        assert db['age'] == 21

        # But, be carefull with more complex objects.
        db['ages'] = [21, 42, 84]
        # Following will not persist the change
        db['ages'].append(168)
        # Correct approach
        temp = db['ages']
        temp.append(168)
        db['ages'] = temp


The writeback option allows object updates in place, but the update is local until the ``sync`` or the ``close`` method is called.:

.. code-block:: python

    with cshelve.open('config.ini', writeback=True) as db:
        # But, be carefull with more complex objects.
        db['ages'] = [21, 42, 84]
        # Persist in memory **only**
        db['ages'].append(168)
        assert db['ages'] == [21, 42, 84, 168]
        # Persisted on the provider
        db.sync()

        # Persisted in memory
        db['ages'].append(336)
        assert db['ages'] == [21, 42, 84, 168, 336]

    # The context manager called the `close` method and persists the data on the provider
    with cshelve.open('config.ini') as db:
        assert db['ages'] == [21, 42, 84, 168, 336]

The updated data is saved to the provider, so any future access will retrieve the updated value.

Deleting Data
+++++++++++++

To delete a key from a *cshelve* database, use the ``del`` statement:

.. code-block:: python

    with cshelve.open('conf.ini') as db:
        db["name"] = "foo"
        # Remove a key-value pair
        del db['name']
        assert 'name' not in db

        # Attempt to retrieve the deleted key (this will raise a KeyError)
        try:
            print(db['preferences'])
        except KeyError:
            print("Key 'preferences' not found")


Deleting a key-value pair removes it from is provider, freeing up space and ensuring it's no longer accessible.

Working with Custom Objects
+++++++++++++++++++++++++++

*cshelve* allows storing custom Python objects as well, making it suitable for applications that need to persist complex data structures.

.. code-block:: python

    import cshelve

    class User:
        def __init__(self, username, age):
            self.username = username
            self.age = age

    # Storing a custom object in cshelve
    with cshelve.open('conf.ini') as db:
        db['user1'] = User('Alice', 28)
        db['user2'] = User('Bob', 32)

    # Retrieving and using the stored object
    with cshelve.open('conf.ini') as db:
        user1 = db['user1']
        print(user1.username)  # Output: Alice
        print(user1.age)       # Output: 28

Exactly as the update example, updating a complex object requires a little more care:

.. code-block:: python

    import cshelve

    class User:
        def __init__(self, username, age):
            self.username = username
            self.age = age

    with cshelve.open('conf.ini') as db:
        db['user1'] = User('Alice', 28)

        db['user1'].age = 42
        assert db['user1'].age == 28


Closing the *cshelve* Database
++++++++++++++++++++++++++++++

When using *cshelve*, data is automatically saved when the database is closed. By using a ``with`` statement, as shown in the examples above, *cshelve* will handle opening and closing the connection.

If not using a ``with`` statement, remember to close the database manually:

.. code-block:: python

    db = cshelve.open('conf.ini')
    db['key'] = 'value'
    db.close()  # Make sure to call close() to save changes
