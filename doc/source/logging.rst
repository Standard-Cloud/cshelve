Logging
=======

**cshelve** provides flexible logging options to help monitor and debug applications.
A specific logger can be provided to the `cshelve` object, and the logging capabilities of the underlying storage provider (if applicable) can also be utilized.

Providing a Specific Logger to cshelve
######################################
A custom logger can be passed to the `cshelve.open` function using the `logger` parameter.
This allows control over the logging behavior of `cshelve` independently of the underlying storage provider.

Example:

.. code-block:: python

    import logging
    import cshelve

    # Create a custom logger
    custom_logger = logging.getLogger("my_custom_logger")
    custom_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    custom_logger.addHandler(handler)

    # Pass the custom logger to cshelve
    with cshelve.open('config.ini', logger=custom_logger) as db:
        ...

Using Provider-Specific Logging
###############################
Some storage providers have their own logging capabilities.
Logging for these providers can be enabled and configured separately.
Refer to the provider's documentation for details on configuring logging for that provider.

Example with Azure Blob Storage:

.. code-block:: ini

    [default]
    provider        = azure-blob
    account_url     = https://myaccount.blob.core.windows.net
    auth_type       = passwordless
    container_name  = mycontainer

    # Configure logging for operations on Azure Blob Storage
    [logging]
    http            = true
    credentials     = true

.. code-block:: python

    import logging
    import sys
    import cshelve

    # Set the logging level for the azure.storage.blob library
    azure_logger = logging.getLogger("azure.storage.blob")
    azure_logger.setLevel(logging.DEBUG)

    # Direct logging output to stdout
    handler = logging.StreamHandler(stream=sys.stdout)
    azure_logger.addHandler(handler)

    # Use cshelve with Azure Blob Storage
    with cshelve.open('azure-blob-config-with-logging.ini') as db:
        ...
