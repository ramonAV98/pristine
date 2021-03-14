import pandas_datareader.data as web
import pandas as pd


def load_data(stocks, end_date=None, source='yahoo'):
    """
    :param stocks:
    :param end_date:
    :param source:
    :return:
    """
    start_date = _find_start_end(end_date)

    if source == 'yahoo':
        stocks_data, locate_stock_fn = _yahoo_source(stocks, start_date, end_date)
    else:
        raise ValueError(f"Source '{source}' not available")
    return stocks_data, locate_stock_fn


def _find_start_end(end_date):
    # TODO: load exactly 80 days.
    bdate_range = pd.bdate_range(end=end_date, periods=100)
    start_date = bdate_range[0].strftime('%Y-%m-%d')
    return start_date


def _yahoo_source(stocks, start_date, end_date):
    stocks_data = web.DataReader(stocks, 'yahoo', start_date, end_date)
    stocks_data = stocks_data.swaplevel(0, 1, 1)

    def locate_stock_fn(df, stock):
        df_stock = df.loc[:, stock].copy()
        df_stock.reset_index(inplace=True)
        return df_stock
    return stocks_data, locate_stock_fn

