import pandas_datareader.data as web
import pandas as pd
import numpy as np


def load_data(symbols, end_date, start_date=None, source='yahoo'):
    """
    :param symbols:
    :param end_date:
    :param source:
    :return:
    """
    if start_date is None:
        start_date = _find_start_end(end_date)
    if source == 'yahoo':
        df_source = _yahoo_source(symbols, start_date, end_date)
    else:
        raise ValueError(f"Source '{source}' not available")
    df_source = _clean_df_source(df_source, symbols)
    return df_source


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
    return df_source


def _validate_end_date(self):
    """
    Validates self.end_date corresponds to a business day.
    If self.end_date is None, assigns the most recent business day.
    """
    if self.end_date is None:
        today = pd.Timestamp('today')
        if np.is_busday(today.strftime('%Y-%m-%d')):
            self.end_date = today.strftime('%Y-%m-%d')
        else:
            previous_bday = today - pd.tseries.offsets.BDay(1)
            self.end_date = previous_bday
    else:
        assert np.is_busday(self.end_date.strftime('%Y-%m-%d'))
