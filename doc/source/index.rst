.. cshelve documentation master file, created by
   sphinx-quickstart on Tue Nov 12 07:50:05 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cshelve documentation
=====================

`Cloud Shelve (cshelve)` is a Python package that provides a seamless way to store and manage data in the cloud using the familiar [Python Shelve interface](https://docs.python.org/3/library/shelve.html). It is designed for efficient and scalable storage solutions, allowing you to leverage cloud providers for persistent storage while keeping the simplicity of the `shelve` API.


Table of contents
#################

.. toctree::
   :maxdepth: 1

   introduction
   tutorial
   in-memory
   azure-blob


Install
-------

.. code-block:: console

   $ pip install cshelve


Usage
-----

Locally, `cshelve` works just like the built-in `shelve` module.

.. code-block:: python

   import cshelve

   d = cshelve.open('local.db')  # Open the local database file

   key = 'key'
   data = 'data'

   d[key] = data                 # Store data at the key (overwrites existing data)
   data = d[key]                 # Retrieve a copy of data (raises KeyError if not found)
   del d[key]                    # Delete data at the key (raises KeyError if not found)

   flag = key in d               # Check if the key exists in the database
   klist = list(d.keys())        # List all existing keys (could be slow for large datasets)

   # Note: Since writeback=True is not used, handle data carefully:
   d['xx'] = [0, 1, 2]           # Store a list
   d['xx'].append(3)             # This won't persist since writeback=True is not used

   # Correct approach:
   temp = d['xx']                # Extract the stored list
   temp.append(5)                # Modify the list
   d['xx'] = temp                # Store it back to persist changes

   d.close()                     # Close the database

[Python official documentation of the Shelve module](https://docs.python.org/3/library/shelve.html)

But, `cshelve` also supports cloud storage. You can use the same API to store data in the cloud.
You just need to create an `ini` with your configuration.

Here to use a In-Memory storage to simplify your tests:

.. code-block:: console

   $ cat in-memory.ini
   [default]
   provider    = in-memory


Here to use Azure Blob Storage:

.. code-block:: console

   $ cat azure-blob.ini
   [default]
   provider        = azure-blob
   account_url     = https://myaccount.blob.core.windows.net
   auth_type       = passwordless
   container_name  = mycontainer


.. toctree::
   :maxdepth: 2
   :caption: Contents:

