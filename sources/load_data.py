from sources._yahoo_source import yahoo_source
from datetime import timedelta, date
import numpy as np
import pandas as pd


def load_data(stocks, end_date=None, source='yahoo'):
    """
    :param stocks:
    :param end_date:
    :param source:
    :return:
    """
    print(end_date)
    start_date = _find_start_end(end_date)
    if source == 'yahoo':
        stocks_data, locate_stock_fn = yahoo_source(stocks, start_date, end_date)
    else:
        raise ValueError(f"Source '{source}' not available")
    return stocks_data, locate_stock_fn


def _find_start_end(end_date):
    if isinstance(end_date, str):
        end_date = pd.Timestamp(end_date)
    start_date = end_date - timedelta(days=1)
    while np.busday_count(date.strftime(start_date, '%Y-%m-%d'), date.strftime(end_date, '%Y-%m-%d')) != 40:
        start_date -= timedelta(days=1)
    return start_date
