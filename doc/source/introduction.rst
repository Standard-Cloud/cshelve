Introduction to the *shelve* and *cshelve* Module
=================================================

Python's standard library includes a variety of modules designed to simplify data storage and management. Among them, the *shelve* module stands out as an incredibly versatile tool for simple, file-based data persistence.

The *cshelve* module extends the *shelve* module by adding cloud storage capabilities. It follows the same API, allowing a switch from local storage to cloud storage without modifying the code.


What is the *shelve* Module?
############################

The *shelve* module in Python allows storing Python objects persistently using a dictionary-like interface. Essentially, it creates a persistent, disk-backed dictionary where the keys are strings and the values can be any Python object that can be serialized.

Unlike more complex databases, *shelve* is lightweight and doesn't require defining schemas, writing complicated queries or a database engine. Instead, it's a simple key-value store designed for scenarios needing a quick way to save and retrieve structured data between program runs without the overhead of a full database.

Key Features of *shelve*
************************

- **Dictionary-like Interface**: Interaction with *shelve* objects uses standard dictionary operations, making it familiar and intuitive for Python developers.
- **Automatic Serialization**: *shelve* uses Python's *pickle* module to automatically serialize and deserialize objects. This allows storing complex data structures like lists, dictionaries, and custom objects.
- **Persistent Storage**: Data stored in a *shelve* object remains on disk, so it can be retrieved even after the program exits.
- **Ease of Use**: No setup is required, unlike traditional databases. Just import *shelve*, open a file, and start storing data.

Basic Usage
###########

Here's a basic example of how to use the *shelve* module to store and retrieve data:

.. code-block:: python

    import shelve

    # Open a shelve database file
    with shelve.open('my_shelve_db') as db:
        # Store data in the my_shelve_db file
        db['username'] = 'Alice'
        db['age'] = 28
        db['preferences'] = {'theme': 'dark', 'notifications': True}

        # Retrieve data from the my_shelve_db file
        print(db['username'])  # Output: Alice
        print(db['age'])       # Output: 28
        print(db['preferences'])  # Output: {'theme': 'dark', 'notifications': True}

In this example, we open a shelve file named ``my_shelve_db`` and store several key-value pairs in it. When the file is closed, the data is saved to disk. The next time we open the file, we can access the data in the same way.

Adding and Retrieving Objects
#############################

The real strength of *shelve* lies in its ability to store complex data structures and Python objects:

.. code-block:: python

    import shelve

    class User:
        def __init__(self, username, age):
            self.username = username
            self.age = age

    # Storing a complex object in shelve
    with shelve.open('my_shelve_db') as db:
        db['user1'] = User('Bob', 35)
        db['user2'] = User('Carol', 29)

    # Retrieving and using the stored object
    with shelve.open('my_shelve_db') as db:
        user = db['user1']
        print(user.username)  # Output: Bob
        print(user.age)       # Output: 35


What is the *cshelve* Module?
#############################

The *cshelve* module extends the functionality of the *shelve* module by adding cloud storage capabilities. It allows users to switch seamlessly between local and cloud storage without changing their code.

Key Features of *cshelve*
#########################

- **Unified API**: *cshelve* follows the same API as *shelve*, making it easy to switch between local and cloud storage.
- **Cloud Storage Support**: *cshelve* allows storing data in cloud storage services. Currently, it supports Azure Blob Storage and In-Memory storage.
- **Configuration-based**: Users can specify the storage provider and credentials in an ``.ini`` file, simplifying the setup process. If the provided file extension is not ``.ini``, the file will be opened as an ordinary *shelve* file.
- **An In Memory Provider**: For testing and development purposes without the need to interact with real storage.

Basic Usage
###########

Because *cshelve* follows the same API as *shelve*, we can use the same example as before to demonstrate its usage. The only difference is that we need to provide an **INI** configuration file specifying the storage provider.

Here's an example of the ``in-memory`` storage configuration:

.. code-block:: console

    $ cat in-memory.ini
    [default]
    provider    = in-memory

Then the same examples as before but using *cshelve*:

.. code-block:: python

    import cshelve

    with cshelve.open('in-memory.ini') as db:
        # Store data in memory
        db['username'] = 'Alice'
        db['age'] = 28
        db['preferences'] = {'theme': 'dark', 'notifications': True}

        # Retrieve data
        print(db['username'])     # Output: Alice
        print(db['age'])          # Output: 28
        print(db['preferences'])  # Output: {'theme': 'dark', 'notifications': True}


Using an Cloud Storage
######################

Let's now see how to use Azure Blob Storage with *cshelve*.

To do so, the prerequisites are:

- An Azure account

- An Azure Storage account

- Permission to create a container in the Azure Storage account

- Optionally, the Azure CLI installed on your machine


Here's an example of the `Azure Blob Storage` configuration:

.. code-block:: console

    $ cat azure-blob.ini
    [default]
    provider        = azure-blob
    account_url     = https://myaccount.blob.core.windows.net
    # Another auth type are available on the Azure Blob Storage provider documentation.
    auth_type       = passwordless
    container_name  = mycontainer


Then the same example as before but using *cshelve* with Azure Blob Storage:

.. code-block:: python

    import cshelve

    with cshelve.open('azure-blob.ini') as db:
        # Store data in the Azure Blob Storage
        db['username'] = 'Alice'
        db['age'] = 28
        db['preferences'] = {'theme': 'dark', 'notifications': True}

        # Retrieve data from the Azure Blob Storage
        print(db['username'])  # Output: Alice
        print(db['age'])       # Output: 28
        print(db['preferences'])  # Output: {'theme': 'dark', 'notifications': True}


Using `Pathlib`
###############

The `Pathlib` module is a Python module that provides an object-oriented interface for working with the file system.
Not all Python versions support the `Pathlib` module with `shelve`, but `cshelve` does.

.. code-block:: python

    import cshelve

    with cshelve.open(Path('in-memory.ini')) as db:
        ...

    with cshelve.open(Path('local-shelve.db')) as db:
        ...

    with cshelve.open(Path('azure-blob.ini')) as db:
        ...


Advanced Usage
##############

Environment variable in TOML
############################

Nativelly, TOML doesn't allow the replacement of string by environment variable.
Because it's a frequent use case, `cshelve` defined its convention to do so.
Consequently, string starting by `$` are considered as passed via environment variable.

Examples:

In the following example, `cshelve` retrieve the `ACCOUNT_ID` and the `CONTAINER` from environment variables.
If they are not defined, an exception is raised.

.. code-block:: console

    $ cat azure-blob.ini
    [default]
    provider        = azure-blob
    account_url     = $ACCOUNT_ID
    auth_type       = passwordless
    container_name  = $CONTAINER


Custom parameters for the provider
##################################

The `provider_params` parameter allows users to pass custom parameters to the underlying storage provider via code or TOML.
This can be useful for configuring specific provider options that are not covered by the default configuration.

Using code
**********

For example, when using the `azure-blob` provider, you can pass parameters like `secondary_hostname`, `max_block_size`, or `use_byte_buffer`.

.. code-block:: python

    import cshelve

    provider_params = {
        'secondary_hostname': 'https://secondary.blob.core.windows.net',
        'max_block_size': 4 * 1024 * 1024,  # 4 MB
        'use_byte_buffer': True
    }

    with cshelve.open('azure-blob.ini', provider_params=provider_params) as db:
        ...


Using TOML
**********

String can be passed via TOML by defining the `provider_params` section.
When code and TOML are defined, the TOML override the code configuration.

.. code-block:: console

    $ cat azure-blob.ini
    [default]
    provider        = azure-blob
    account_url     = https://myaccount.blob.core.windows.net
    auth_type       = passwordless
    container_name  = mycontainer

    [provider_params]
    secondary_hostname = 'https://secondary.blob.core.windows.net


.. code-block:: python

    import cshelve

    provider_params = {
        'secondary_hostname': 'Override by the TOML',
        'max_block_size': 4 * 1024 * 1024,  # 4 MB
        'use_byte_buffer': True
    }

    with cshelve.open('azure-blob.ini', provider_params=provider_params) as db:
        ...
