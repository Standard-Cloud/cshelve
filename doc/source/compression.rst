Compression Configuration
=========================

*cshelve* supports compression to reduce the size of stored data.
This is particularly useful when working with large datasets or to reduce network time.
The compression algorithm can be configured using a configuration file.

Configuration File
##################

The compression settings are specified in an INI file.
Below is an example configuration file named `config.ini`:

.. code-block:: ini

    [default]
    provider        = in-memory
    persist-key     = compression
    exists          = true

    [compression]
    algorithm   = zlib
    level       = 1

In this example, the `algorithm` is set to `zlib`, and the `compression level <https://docs.python.org/3/library/zlib.html>`_ is set to `1`.

Supported Algorithms
#####################

Currently, *cshelve* supports the following compression algorithms:

- `zlib`: A widely-used compression library.

Using Compression
#################

Once compression is configured as previously in the `config.ini` file, it will automatically compress data before storing it and decompress data when retrieving it.
The application code doesn't need to be updated:

.. code-block:: python

    import cshelve

    with cshelve.open('config.ini') as db:
        db['data'] = 'This is some data that will be compressed.'

    with cshelve.open('config.ini') as db:
        data = db['data']
        print(data)  # Output: This is some data that will be compressed.

In this example, the data is compressed before being stored and decompressed when retrieved, thanks to the configuration.

Error Handling
##############

If an unsupported compression algorithm is specified, *cshelve* will raise an `UnknownCompressionAlgorithmError`.
Ensure that the algorithm specified in the configuration file is supported.
