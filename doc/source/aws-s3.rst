AWS S3 provider
===============

AWS S3 Bucket is a cloud storage solution for data storage and retrieval that is highly available, secure, durable, and scalable.
*cshelve* can be configured to use AWS S3 Bucket as a provider for storing and retrieving data.

Installation
############

To install the *cshelve* package with AWS S3 support, run the following command:

.. code-block:: console

  $ pip install cshelve[aws-s3]

Configuration Options
#####################

The following table lists the configuration options available for the AWS S3 provider:

.. list-table::
  :header-rows: 1

  * - Scope
    - Option
    - Description
    - Required
  * - ``default``
    - ``bucket_name``
    - The name of the S3 Bucket.
    - Yes
  * - ``default``
    - ``auth_type``
    - The authentication method to use: ``access_key``.
    - Yes
  * - ``default``
    - ``key_id``
    - The AWS key ID.
    - Yes
  * - ``default``
    - ``key_secret``
    - The AWS key secret.
    - Yes

Permissions
###########

Depending on the ``open`` flag, the permissions required by *cshelve* for S3 storage vary:

.. list-table::
  :header-rows: 1

  * - Flag
    - Description
    - Permissions Needed
  * - ``r``
    - Open an existing S3 bucket for reading only.
    - `AmazonS3ReadOnlyAccess <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3ReadOnlyAccess.html>`_
  * - ``w``
    - Open an existing S3 bucket for reading and writing.
    - `AmazonS3ReadWriteAccess <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html>`_
  * - ``c``
    - Open a S3 bucket for reading and writing, creating it if it doesn't exist.
    - `AmazonS3FullAccess <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3FullAccess.html>`_
  * - ``n``
    - Purge the S3 bucket before using it.
    - `AmazonS3FullAccess <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonS3FullAccess.html>`_

Access Key Authentication
+++++++++++++++++++++++++

Currently, only the Access Key auth is supported.
The secret can be set as an environment variable, and the key must be defined in the configuration.

.. code-block:: console

  $ cat access-key.ini
  [default]
  provider        = aws-s3
  bucket_name     = cshelve
  auth_type       = access_key
  # Here the environment variable containing the key is named AWS_KEY_ID and the secret AWS_KEY_SECRET.
  key_id          = $AWS_KEY_ID
  key_secret      = $AWS_KEY_SECRET

Configure the Boto3 Client
##########################

Behind the scenes, this provider uses the `Boto3 Client <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html>`_.
Users can pass specific parameters using the `provider_params` parameter of the `cshelve.open` function and in the configuration file.

Here is an example where `endpoint_url` is specified using `provider_params`:

.. code-block:: python

  import cshelve

  provider_params = {'endpoint_url': 'http://localhost:9000'}

  with cshelve.open('aws-s3.ini', provider_params=provider_params) as db:
  ...

Here is an example where `endpoint_url` is specified using the configuration file:

.. code-block:: console

  $ cat aws-s3.ini
  [default]
  provider        = aws-s3
  bucket_name     = cshelve
  auth_type       = access_key
  key_id          = $AWS_KEY_ID
  key_secret      = $AWS_KEY_SECRET

  [provider_params]
  endpoint_url = "http://localhost:9000"

.. code-block:: python

  import cshelve

  with cshelve.open('aws-s3.ini') as db:
  ...
