Azure Blob Storage is a cloud storage solution for data storage and retrieval that is highly available, secure, durable, and scalable.
*cshelve* can be configured to use Azure Blob Storage as a provider for storing and retrieving data.

Installation
############
.. code-block:: console

    $ pip install cshelve[azure-blob]

Options
#######
.. list-table::
    :header-rows: 1

    * - Scope
      - Option
      - Description
      - Required
    * - ``default``
      - ``account_url``
      - The URL of your Azure storage account.
      - No
    * - ``default``
      - ``auth_type``
      - The authentication method to use: ``access_key``, ``passwordless``, ``connection_string`` or ``anonymous``.
      - Yes
    * - ``default``
      - ``container_name``
      - The name of the container in your Azure storage account.
      - Yes
    * - ``logging``
      - ``http``
      - Enabling HTTP logging for all operations on the blob storage.
      - No
    * - ``logging``
      - ``credentials``
      - Enabling HTTP logging for a credential operations.
      - No

Depending on the ``open`` flag, the permissions required by *cshelve* for blob storage vary.

.. list-table::
    :header-rows: 1

    * - Flag
      - Description
      - Permissions Needed
    * - ``r``
      - Open an existing blob storage container for reading only.
      - `Storage Blob Data Reader <https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-reader>`_
    * - ``w``
      - Open an existing blob storage container for reading and writing.
      - `Storage Blob Data Contributor <https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor>`_
    * - ``c``
      - Open a blob storage container for reading and writing, creating it if it doesn't exist.
      - `Storage Blob Data Contributor <https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor>`_
    * - ``n``
      - Purge the blob storage container before using it.
      - `Storage Blob Data Contributor <https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#storage-blob-data-contributor>`_

Logging Configuration
#####################
The logging configuration allows you to enable HTTP logging for all operations on the blob storage and credential operations.
This can be useful for debugging and monitoring purposes
Note that you must set the logging handler to see the logging output.
You can find more details about logging configuration in the `Azure SDK logging documentation <https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-logging#example-logging-output>`_.

Example Configuration
#####################
Here is an example of an INI file with logging configuration:

.. code-block:: ini

    [default]
    provider        = azure-blob
    account_url     = https://myaccount.blob.core.windows.net
    auth_type       = passwordless
    container_name  = mycontainer

    [logging]
    http            = true
    credentials     = true

To see the logging output, you need to set the logging handler in your code:

.. code-block:: python

    import logging
    import sys
    import cshelve

    # Set the logging level for the all the azure libraries.
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)

    # Direct logging output to stdout. Without adding a handler,
    # no logging output is visible.
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    # The usual cshelve usage remains the same.
    with cshelve.open('config-with-logging.ini', 'r') as db:
        ...

Authentication Examples
#######################
An access key can also be used for authentication. You can use either a Shared Access Signature (SAS) or an Access Key.
The secret must be set in an environment variable, and the key must be defined in the configuration.

.. code-block:: console

    $ cat access-key.ini
    [default]
    provider        = azure-blob
    account_url     = https://dscccccccccccccc.blob.core.windows.net
    auth_type       = access_key
    # Here the environment variable containing the access key is named AZURE_STORAGE_ACCESS_KEY.
    environment_key = AZURE_STORAGE_ACCESS_KEY
    container_name  = test-account-key

A connection string can also be used for authentication.
The connection string must be set in an environment variable, and the key must be defined in the configuration.

.. code-block:: console

    $ cat connection-string.ini
    [default]
    provider        = azure-blob
    auth_type       = connection_string
    # Here the environment variable containing the connection string is named AZURE_STORAGE_CONNECTION_STRING.
    environment_key = AZURE_STORAGE_CONNECTION_STRING
    container_name  = test-connection-string

The anonymous authentication method can be used to access public containers, but the authentication does not allow writing data.

.. code-block:: console

    $ cat anonymous.ini
    [default]
    provider        = azure-blob
    account_url     = https://myaccount.blob.core.windows.net
    auth_type       = anonymous
    container_name  = public-container
