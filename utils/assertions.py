def assert_columns(df, cols):
    if isinstance(cols, str):
        cols = [cols]
    for c in cols:
        assert c in df, f'Column {c} not found in dataframe. Needed columns: {cols}'


def assert_type(object, t, object_label):
    assert isinstance(object, t), f'{object_label} must be type {t.__name__}. Instead got {type(object).__name__}'