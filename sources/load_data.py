import pandas_datareader.data as web
import pandas as pd


def load_data(symbols, end_date=None, source='yahoo'):
    """
    :param symbols:
    :param end_date:
    :param source:
    :return:
    """
    start_date = _find_start_end(end_date)

    if source == 'yahoo':
        loc_fn = _yahoo_source(symbols, start_date, end_date)
    else:
        raise ValueError(f"Source '{source}' not available")
    return loc_fn


def _find_start_end(end_date):
    # TODO: load exactly 80 days.
    bdate_range = pd.bdate_range(end=end_date, periods=100)
    start_date = bdate_range[0].strftime('%Y-%m-%d')
    return start_date


def _yahoo_source(symbols, start_date, end_date):
    df_syms_data = web.DataReader(symbols, 'yahoo', start_date, end_date)
    df_syms_data = df_syms_data.swaplevel(0, 1, 1)

    def loc_fn(sym):
        """
        Locates data for a single symbol
        """
        df_sym = df_syms_data.loc[:, sym].copy()
        df_sym.reset_index(inplace=True)
        return df_sym
    return loc_fn

