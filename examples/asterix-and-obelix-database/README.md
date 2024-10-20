# Asterix and Obelix database

This application is a simple database for the Asterix and Obelix comic series. It allows you to add new users to the database, dump the current users in the database, and clear the database.

## Installation

1. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Configure the application to use either local storage or an Azure Container with passwordless or connection string authentication:
    - For local storage, no configuration is needed.
    - For passwordless authentication, use the configuration in [azure-passwordless.ini](./azure-passwordless.ini).
    - For connection string authentication, use the configuration in [azure-connection-string.ini](./azure-connection-string.ini) and set up the environment variables as shown in [.env.example](.env.example).

**Note:** Connection string authentication is faster than passwordless authentication at startup. The impact is measurable in the tests.

## Usage

### Running the Application

To use the application, run the following command:
```bash
python main.py <database-file> dump|save|clear
```
- `<database-configuration>`: The path to the database file.
- `dump`: Print all the users in the database.
- `save`: Add new users to the database.
- `clear`: Clear the database.

### Running the Tests (Unix-like only)

To run the tests, execute the `run-test.sh` script:
```bash
./run-test.sh
```
This script will run a series of tests to ensure that the database operations are working correctly.

## Data

All data used for testing is located in the `datasets` folder.
