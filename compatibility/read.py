import sys

import cshelve


version = sys.argv[1]

with cshelve.open("./azure-passwordless.ini") as db:
    assert db[f"compatibility-{version}"] == f"my complex data from version {version}"
