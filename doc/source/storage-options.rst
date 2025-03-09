Storage Options
===============

When using `cshelve`, you have full control over how data is stored and retrieved.
By default, `cshelve` uses `pickle` to serialize and deserialize Python objects, but it also allows users to store raw bytes, enabling compatibility with various data formats such as JSON, Parquet, CSV, and more.

This page provides an in-depth look at these options, their advantages, and how to configure them.

-----------------------------
Storage Configuration Fields
-----------------------------

To customize storage behavior, two key options are available:

**1. `use_pickle` (Data Format Control)**

- **Description**: Controls whether `cshelve` should use `pickle` for serialization.
- **Default**: `True` (data is pickled by default).
- **When Enabled**: Python objects are automatically serialized and deserialized using `pickle`. This is useful when working exclusively within Python.
- **When Disabled**: Data is stored as raw bytes. Users must convert data into bytes before storing and back after retrieval.
- **Example Usage**:

  .. code-block:: ini

    # file: storage.ini
    [default]
    provider        = ...
    auth_type       = ...
    use_pickle      = false

  .. code-block:: python

    import json
    import cshelve

    data = {"key": "value", "number": 42}
    with cshelve.open('storage.ini') as db:
        db['my_json'] = json.dumps(data).encode()  # Convert to bytes

    with cshelve.open('storage.ini') as db:
        retrieved_data = json.loads(db['my_json'].decode())  # Decode back to JSON

    print(retrieved_data)

- **Why Disable `use_pickle`?**
  - Ensures stored data can be used in other languages.
  - Avoids Python-specific serialization overhead.

- **Important Note:**
  Even if the format is readable in other languages, `cshelve` adds some metadata to the stored data. To disable this metadata use the `use_versioning` option.

**2. `use_versioning` (Data Versioning and Metadata Management)**

- **Description**: Enables versioning for stored data, allowing `cshelve` to manage data evolution.
- **Default**: `True` (versioning is enabled by default).
- **Purpose**:
  - Adds metadata for tracking versions of stored data.
  - Facilitates upgrades from one data version to another.
  - Helps maintain consistency in long-term storage solutions.
- **Example Usage**:

  .. code-block:: ini

    # file: storage.ini
    [default]
    provider        = ...
    auth_type       = ...
    use_versionning = false

  .. code-block:: python

    import cshelve

    with cshelve.open('storage.ini') as db:
        db['my_data'] = b"Raw binary data"

- **Why Enable `use_versioning`?**
  - Provides structured metadata to facilitate future data management.
  - Ensures smooth upgrades between versions.
  - Helps maintain data integrity in evolving storage environments.

- **Why Disable `use_versioning`?**
  - Reduces metadata overhead (compute + storage) for simple data storage.
  - Suitable for short-term storage or non-evolving data.
  - Simplifies the data structure for external use.

-----------------------------
Practical Use Cases
-----------------------------

### **Scenario 1: Storing JSON Data for External Use**
- **Goal**: Store JSON data in the cloud and retrieve it without requiring Python.
- **Configuration**: `use_pickle=False` to store data as raw JSON bytes.
- **Example**:

  .. code-block:: ini

    # file: storage.ini
    [default]
    provider        = ...
    auth_type       = ...
    use_pickle      = false
    use_versionning = false

  .. code-block:: python

    import json
    import cshelve

    data = {"name": "Alice", "score": 95}
    with cshelve.open('storage.ini') as db:
        db['student_data'] = json.dumps(data).encode()

    with cshelve.open('storage.ini') as db:
        retrieved = json.loads(db['student_data'].decode())
    print(retrieved)  # Output: {'name': 'Alice', 'score': 95}

### **Scenario 2: Storing and Retrieving Parquet Files**
- **Goal**: Save structured data in a Parquet file format usable by all Parquet Loader.
- **Configuration**: `use_pickle=False` to store the Parquet file as raw bytes.
- **Example**:

  .. code-block:: ini

    # file: storage.ini
    [default]
    provider        = ...
    auth_type       = ...
    use_pickle      = false
    use_versionning = false

  .. code-block:: python

    import pandas as pd
    import cshelve

    df = pd.DataFrame({"id": [1, 2, 3], "value": ["A", "B", "C"]})
    parquet_bytes = df.to_parquet()

    with cshelve.open('storage.ini') as db:
        db['dataset'] = parquet_bytes

    with cshelve.open('storage.ini') as db:
        retrieved_df = pd.read_parquet(db['dataset'])

    print(retrieved_df)

-----------------------------
Conclusion
-----------------------------

By configuring `use_pickle` and `use_versioning`, users can tailor `cshelve` to their specific storage needs.
Whether optimizing for performance, ensuring interoperability, or future-proofing data management, these options provide significant flexibility and control.

This level of control ensures `cshelve` can serve a wide range of applications, from simple key-value storage to advanced cloud-based data management solutions.
