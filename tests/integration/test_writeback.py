import cshelve


def test_writeback():
    config_file = "tests/configurations/azure-integration/standard.ini"
    key_pattern = "test_writeback"
    data_pattern = [1]

    def _write_data():
        db = cshelve.open(config_file)

        for i in range(100):
            db[f"{key_pattern}{i}"] = data_pattern

        db.close()

    def update_data(writeback):
        db = cshelve.open(config_file, writeback=writeback)

        for i in range(100):
            key = f"{key_pattern}{i}"
            value = db[key]
            value.append(i)

            if writeback:
                assert db[key] == data_pattern + [i]
            else:
                assert db[key] == data_pattern

        db.close()

    def read_data(contains_index):
        db = cshelve.open(config_file)

        for i in range(100):
            key = f"{key_pattern}{i}"
            if contains_index:
                assert db[key] == data_pattern + [i]
            else:
                assert db[key] == data_pattern

        db.close()

    def del_data():
        db = cshelve.open(config_file)

        for i in range(100):
            del db[f"{key_pattern}{i}"]

        db.close()

    # Write default data.
    _write_data()
    # Update data with writeback=False, so data must not be updated.
    update_data(writeback=False)
    # Ensure data was not updated.
    read_data(contains_index=False)
    # Update data with writeback=True, so data must be updated.
    update_data(writeback=True)
    # Ensure data was updated.
    read_data(contains_index=True)
    del_data()
