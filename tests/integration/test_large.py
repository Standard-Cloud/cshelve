import numpy as np
import pandas as pd

import cshelve


def test_large():
    db = cshelve.open('tests/configurations/integration-azure.ini')

    key_pattern = 'test_large'

    # 167.46 MiB
    df = pd.DataFrame(np.random.randint(0, 100, size=(844221, 26)), columns=list('ABCDEFGHIGKLMNOPQRSTUVWXYZ'))

    db[key_pattern] = df
    new_df = db[key_pattern]

    assert id(new_df) != id(df)
    assert new_df.equals(df)
