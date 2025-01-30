import sys

import cshelve


cshelve_version = sys.argv[1]
python_version = sys.argv[2]

with cshelve.open("./azure-passwordless.ini") as db:
    assert (
        db[f"compatibility-{cshelve_version}-{python_version}"]
        == f"my complex data from cshelve version {cshelve_version} and python {python_version}"
    )
