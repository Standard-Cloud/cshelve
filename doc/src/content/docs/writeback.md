---
title: The Writeback Parameter
description: What is the Writeback Parameter?
---

The `writeback` argument in `cshelve` controls how modifications to objects stored in the database are persisted. By default, `writeback` is set to `False`, meaning only explicit updates to the database are written back. When `writeback` is enabled (`True`), changes to mutable objects are cached in memory and persisted upon synchronization or closure.

## Default Behavior (`writeback=False`)

When `writeback` is `False`, changes to mutable objects retrieved from the database are **not** automatically saved. Explicit writes are required to persist updates:

```python
with cshelve.open('provider.ini', writeback=False) as db:
    db['numbers'] = [1, 2, 3]
    numbers = db['numbers']
    numbers.append(4)  # Only changes the in-memory object

    print(db['numbers'])  # Output: [1, 2, 3]

    # Persist changes explicitly:
    db['numbers'] = numbers
```

## Enabling `writeback=True`

With `writeback=True`, `cshelve` caches all retrieved objects in memory. Modifications are saved back to the database upon calling `sync()` or closing the database:

```python
with cshelve.open('provider.ini', writeback=True) as db:
    db['numbers'] = [1, 2, 3]
    numbers = db['numbers']
    numbers.append(4)  # Changes cached object

    print(db['numbers'])  # Output: [1, 2, 3, 4]
```

Changes stay cached until synchronization occurs:

```python
with cshelve.open('provider.ini', writeback=True) as db:
    db['numbers'] = [1, 2, 3]
    db['numbers'].append(4)

    db.sync()  # Explicitly persist changes
```

## Advantages of `writeback=True`

- Automatic tracking and persistence of mutable object changes.
- Reduces explicit reassignment of modified objects.
- Improved performance for frequent small updates until synchronization.

## Disadvantages of `writeback=True`

- Increased memory usage due to cached objects.
- Requires manual synchronization or closing to persist changes.
- Potential for increased memory usage until synchronization occurs.
