import pandas_datareader.data as web
import pandas as pd
import numpy as np

SECTOR_DF_PATH = 'csv/sect_df.csv'


def load_data(symbols, end_date, start_date=None, source='yahoo'):
    """
    :param symbols:
    :param end_date:
    :param source:
    :return:
    """
    _validate_end_date(end_date)
    if start_date is None:
        start_date = _find_start_end(end_date)
    if source == 'yahoo':
        df_source = _yahoo_source(symbols, start_date, end_date)
    else:
        raise ValueError(f"Source '{source}' not available")
    df_source = _clean_df_source(df_source, symbols)
    df_source = _merge_sector(df_source)
    df_source.sort_values(['Symbol', 'Date'], inplace=True)
    df_source.reset_index(drop=True, inplace=True)
    return df_source


def _merge_sector(df_source):
    df_sector = pd.read_csv(SECTOR_DF_PATH, header=0, index_col=0)
    df_sector.dropna(inplace=True)
    df_merge = pd.merge(df_source, df_sector, on='Symbol', how='inner')
    return df_merge


def _find_start_end(end_date):
    # TODO: load exactly 80 days.
    bdate_range = pd.bdate_range(end=end_date, periods=100)
    start_date = bdate_range[0].strftime('%Y-%m-%d')
    return start_date


def _yahoo_source(symbols, start_date, end_date):
    df_source = web.DataReader(symbols, 'yahoo', start_date, end_date)
    df_source = df_source.swaplevel(0, 1, 1)
    return df_source


def _clean_df_source(df_source, symbols):
    dfs = []
    for sym in symbols:
        df_sym = df_source.loc[:, sym]
        df_sym['Symbol'] = sym
        dfs.append(df_sym)
    df_source = pd.concat(dfs).reset_index()
    df_source.dropna(inplace=True)
    _drop_zero_volume(df_source)

    return df_source


def _drop_zero_volume(df_source):
    drop_idx = df_source.loc[df_source['Volume'] == 0].index
    df_source.drop(drop_idx, inplace=True)


def _validate_end_date(end_date):
    """
    Validates self.end_date corresponds to a business day.
    """
    assert np.is_busday(end_date.strftime('%Y-%m-%d'))
