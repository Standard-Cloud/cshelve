import sys
from typing import Optional
import cshelve


unique_key = sys.platform + str(sys.version_info.minor)


def write_data(db_config: str, key_pattern: str, data_pattern: str):
    """
    Write data to the DB.
    """
    db = cshelve.open(db_config)

    for i in range(100):
        db[f"{key_pattern}{i}"] = f"{data_pattern}{i}"

    db.close()


def del_data(config_file: str, key_pattern: Optional[str] = None):
    """
    Delete data from the DB.
    """
    db = cshelve.open(config_file)

    if key_pattern is None:
        for i in db:
            del db[i]
    else:
        for i in range(100):
            del db[f"{key_pattern}{i}"]

    db.close()
