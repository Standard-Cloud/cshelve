def write_same_key(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100):
    db['element'] = i

db.close()
"""


def delete_same_key(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100):
    db['element'] = i
    del db['element']

db.close()
"""


def write_several_keys(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100000):
    db['element' + str(i)] = i

db.close()
"""


def delete_several_keys(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100000):
    k = 'element' + str(i)
    db[k] = i
    del db[k]

db.close()
"""


def read_same_key(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100000):
    db['element'] = 0
    r = db[f'element']

db.close()
"""


def read_several_keys(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100000):
    k = 'element' + str(i)
    db[k] = i
    r = db[k]

db.close()
"""


def iterate_several_keys(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100000):
    k = 'element' + str(i)

for i in range(100000):
    for i in db:
        ...

db.close()
"""


def len_several_keys(db_filename: str):
    return f"""
import cshelve

db = cshelve.open('{db_filename}', 'n')

for i in range(100000):
    k = 'element' + str(i)

for i in range(100000):
    _ = len(db)

db.close()
"""


performance_tests = {
    "write_same_key": write_same_key,
    "write_several_keys": write_several_keys,
    "read_same_key": read_same_key,
    "read_several_keys": read_several_keys,
    "delete_same_key": delete_same_key,
    "delete_several_keys": delete_several_keys,
    "iterate_several_keys": iterate_several_keys,
    "len_several_keys": len_several_keys,
}
