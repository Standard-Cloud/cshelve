in-memory provider
==================

For testing and development purposes, it is useful to have an in-memory provider.
This provider is not persistent and will be lost when the program ends, but it allows some tests to be done without the need to create real storage.

Installation
############

This provider is included in the package and does not require any additional installation.

Options
#######

| Option         | Description                                                                  | Required | Default Value |
|----------------|------------------------------------------------------------------------------|----------|---------------|
| `persist-key`  | If set, its value will be conserved and reused during the program execution. | :x:      | None          |
| `exists`       | If True, the database exists; otherwise, it will be created.                 | :x:      | False         |

Note: The `exists` option is mainly for internal testing of `cloud-shelve`.

Configuration example
#####################

.. code-block:: console

    $ cat in-memory.ini
    [default]
    provider    = in-memory
    persist-key = True
    exists      = True
