import pandas_datareader.data as web


def yahoo_source(stocks, start_date, end_date):
    stocks_data = web.DataReader(stocks, 'yahoo', start_date, end_date)
    stocks_data = stocks_data.swaplevel(0, 1, 1)

    def locate_stock_fn(df, stock):
        df_stock = df.loc[:, stock].copy()
        df_stock.reset_index(inplace=True)
        df_stock.sort_values('Date', inplace=True)
        _add_ma_to_dataframe(df_stock)
        return df_stock

    return stocks_data, locate_stock_fn


def _add_ma_to_dataframe(df):
    """
    :warning: inplace operation
    :param df:
    :return:
    """
    assert 'Adj Close' in df, 'Ajd Close column not found. Cannot compute ma'
    df.loc[:, '20ma'] = df.loc[:, 'Adj Close'].rolling(window=20, min_periods=0).mean()
    df.loc[:, '40ma'] = df.loc[:, 'Adj Close'].rolling(window=40, min_periods=0).mean()
