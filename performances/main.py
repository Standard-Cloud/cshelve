import sys
import timeit
import cshelve
import datetime
from concurrent.futures import ThreadPoolExecutor

from tests import performance_tests


BACKENDS = [
    # Run test locally.
    "local",
    # Run test using Azure Blob Storage.
    "test-azure.ini",
]

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
            "commit_hash": COMMIT_HASH,
        }
    )

    # Save the result in the DB.
    db[backend_name] = backend_perfs


def run_test(db, backend):
    # Test are saved in the DB using the following key:
    res_key = f"{backend}--{OS_TYPE}--{PYTHON_MAJOR_VERSION}"

    for name, fct in performance_tests.items():
        print(
            f"Running test {name} for backend {backend} on {OS_TYPE} with Python {PYTHON_MAJOR_VERSION}.",
            flush=True,
        )
        # Purge the DB used by tests.
        cshelve.open(backend, "n").close()
        # Execute the test providing the backend to test.
        res_test_perf = fct(backend)
        exec_time = timeit.timeit(res_test_perf, number=10)
        # Save the result in the DB.
        save(db, res_key, name, exec_time)


with cshelve.open(database_name) as db:
    # Run the tests for each backend and save the results in the result DB.
    # Because backend are independent, we can run them in parallel.
    # It may have an impact on the network, but currently the number of backend is limited.
    # with ThreadPoolExecutor(max_workers=len(BACKENDS)) as executor:
    #     list(executor.map(lambda backend: run_test(db, backend), BACKENDS))

    # Simpli display the results.
    print("Results:")
    for backend, res in db.items():
        for fct_name, res in res.items():
            if len(res) > 1:
                previous = res[-2]["exec_time"] if len(res) > 1 else 0
                current = res[-1]["exec_time"]
                perf_result = (
                    f"better: -({previous - current:.2f})"
                    if current < previous
                    else f"worst (+{current - previous:.2f})"
                )
                print(
                    f"Backend: {backend}, Function: {fct_name}, diff performance are {perf_result}"
                )
            else:
                print(
                    f"No previous performance to compare with for backend {backend}, Function {fct_name}."
                )
