Encryption Configuration
=========================

The `cshelve` module supports encrypting data before it is sent to the storage provider.
This feature is particularly useful for ensuring data integrity and mitigating potential security risks associated with pickles.

.. note::
   Only the values (pickled data) are encrypted, not the keys.

.. caution::
   Encryption is CPU-intensive and may impact performance.

Installation
############

Encryption functionality is not included by default. To enable encryption, install the additional dependencies by running:

.. code-block:: console

   $ pip install cshelve[encryption]

Configuration File
##################

Encryption settings are defined in an INI file. Below is an example configuration file named `config.ini`:

.. code-block:: ini

   [default]
   provider        = in-memory
   persist-key     = compression
   exists          = true

   [encryption]
   algorithm   = aes256
   # Development configuration: encryption key stored directly in the file.
   key         = Sixteen byte key

In this example, the encryption algorithm is set to `aes256`, and the encryption key is defined as `my encryption key`.

Using Environment Variables for Keys
####################################

For improved security, it is recommended to avoid storing encryption keys directly in configuration files. Instead, use an environment variable to supply the key.
Here's an updated example using an environment variable named `ENCRYPTION_KEY`:

.. code-block:: ini

   [default]
   provider        = in-memory
   persist-key     = compression
   exists          = true

   [encryption]
   algorithm   = aes256
   # The encryption key is retrieved from the environment variable `ENCRYPTION_KEY`.
   environment_key = ENCRYPTION_KEY

Supported Algorithms
#####################

Currently, `cshelve` supports the following encryption algorithm:

- **`aes256`**: A widely-used symmetric encryption standard.

Using Encryption
#################

Once encryption is configured in the `config.ini` file, data will automatically be encrypted before storage and decrypted upon retrieval. No changes are required in the application code. For example:

.. code-block:: python

   import cshelve

   # Writing encrypted data
   with cshelve.open('config.ini') as db:
       db['data'] = 'This is some data that will be encrypted.'

   # Reading encrypted data
   with cshelve.open('config.ini') as db:
       data = db['data']
       print(data)  # Output: This is some data that will be encrypted.

In this example, the data is transparently encrypted when stored and decrypted when retrieved, as specified in the configuration.

Error Handling
##############

If an unsupported encryption algorithm is specified in the configuration file, cshelve will raise an `UnknownEncryptionAlgorithmError`. Additionally, the following errors may occur:

- `MissingEncryptionKeyError`: Raised when no encryption key is provided for encryption.

- `EncryptedDataCorruptionError`: Raised when the encrypted data is found to be corrupted during decryption.

Ensure that the algorithm listed in the config.ini file matches one of the supported options and that the encryption key is correctly provided.
