import sys
import timeit
import cshelve
import datetime

from tests import performance_tests


BACKENDS = ["local", "test-azure.ini"]

# The database containing the result of the tests.
database_name = sys.argv[1]

# Retrieve the OS type, the Python version and the commit hash.
# Those information allows to track performance on different platforms.
# If not provided an default version is used to allow test.
if len(sys.argv) > 2:
    OS_TYPE = sys.argv[2]
    PYTHON_MAJOR_VERSION = sys.argv[3]
    COMMIT_HASH = sys.argv[4]
else:
    OS_TYPE = "unknown"
    PYTHON_MAJOR_VERSION = "unknown"
    COMMIT_HASH = "unknown"


def save(db, backend_name, fct_name, exec_time):
    """
    Save the result of a performance test in the database.

    Data is stored in the following format:
    {
        '<backend_name>': {
            '<fct_name>': [
                {
                  'exec_time': <exec_time>,
                  'datetime': <datetime>,
                  'os': '<os_type>',
                  'python_major_version': '<python_major_version>',
                  'commit_hash': '<commit_hash>'
                }
                ...
            ],
            ...
        },
        ...
    }
    """
    # Add the backend in the DB if not exists.
    if backend_name not in db:
        db[backend_name] = {}

    # Retrieve backend data.
    backend_perfs = db[backend_name]
    # Add the res to the backend data
    if fct_name not in backend_perfs:
        backend_perfs[fct_name] = []

    backend_perfs[fct_name].append(
        {
            "exec_time": exec_time,
            "datetime": datetime.datetime.now(),
            "os": OS_TYPE,
            "python_major_version": PYTHON_MAJOR_VERSION,
            "commit_hash": COMMIT_HASH,
        }
    )

    # Save the result in the DB.
    db[backend_name] = backend_perfs


with cshelve.open(database_name) as db:
    # Run the tests for each backend and save the results in the result DB.
    for backend in BACKENDS:
        for name, code in performance_tests.items():
            # Execute the test providing the backend to test.
            res_test_perf = code(backend)
            exec_time = timeit.timeit(res_test_perf, number=10)
            save(db, backend, name, exec_time)

    # Simpli display the results.
    for backend, res in db.items():
        for fct_name, fct_res in res.items():
            for res in fct_res:
                print(backend, fct_name, res)
