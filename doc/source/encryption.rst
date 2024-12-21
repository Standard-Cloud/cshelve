Encryption Configuration
========================

*cshelve* supports data encryption before sending data to the provider.
This is particularly useful when user want to ensure the non modification of the data and reduce potential attacks via pickles.

Installation
############

The encryption functionality is not natively installed, to install it, run:

.. code-block:: console

    $ pip install cshelve[encryption]


Configuration File
##################

The encryption settings are specified in an INI file.
Below is an example configuration file named `config.ini`:

.. code-block:: ini

    [default]
    provider        = in-memory
    persist-key     = compression
    exists          = true

    [encryption]
    algorithm   = aes256
    # Development configuration putting the key in the config file.
    key         = "my encryption key"

In this example, the `algorithm` is set to `aes256`, and the `encryption key` is set to `my encryption key`.

For security purpose its better to not put the key in the config file and use environment variable to provide it.
Here the same example using an environment variable named `ENCRYPTION_KEY`:

.. code-block:: ini

    [default]
    provider        = in-memory
    persist-key     = compression
    exists          = true

    [encryption]
    algorithm   = aes256
    # Here the environment variable containing the encryption key is named ENCRYPTION_KEY.
    environment_key = ENCRYPTION_KEY


Supported Algorithms
#####################

Currently, *cshelve* supports the following encryption algorithms:

- `aes256`: A widely-used symetric encryption library.

Using Encryption
#################

Once encryption is configured as previously in the `config.ini` file, it will automatically crypt data before storing it and decrypt data when retrieving it.
The application code doesn't need to be updated:

.. code-block:: python

    import cshelve

    with cshelve.open('config.ini') as db:
        db['data'] = 'This is some data that will be encrypt.'

    with cshelve.open('config.ini') as db:
        data = db['data']
        print(data)  # Output: This is some data that will be encrypt.

In this example, the data is encrypt before being stored and decrypt when retrieved, thanks to the configuration.

Error Handling
##############

If an unsupported compression algorithm is specified, *cshelve* will raise an `UnknownEncryptionAlgorithmError`.
Ensure that the algorithm specified in the configuration file is supported.
