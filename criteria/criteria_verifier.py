from sources.load_data import load_data
from criteria._buy_criteria import BuyCriteria
from criteria._sell_criteria import sell_criteria
import numpy as np
import pandas as pd


def criteria_verifier(symbols, end_date=None, source='yahoo'):
    """
    Verifies buy and sell criteria for each given stock.

    Parameters
    -----------
    symbols: list. Collection of stock symbols (i.e., tickers).
    end_date: str. Date on which the verification process will take place. If None, defaults to today's date.
    source: str. Source identifier from which stocks data will be obtained. If None, defaults to yahoo source.
    """
    end_date = _validate_end_date(end_date)
    df, locate_stock_fn = load_data(symbols, end_date, source)
    criteria_results = []
    for sym in symbols:
        criteria = _run_criteria_for_stock(df, sym, locate_stock_fn)
        if criteria is None:
            continue
        criteria_results.append(criteria)
    return criteria_results


def _run_criteria_for_stock(df, symbol, locate_stock_fn):
    """
    Runs buy and sell criteria for the given stock data

    :param df: pd.DataFrame. Dataframe containing for all symbol
    :param symbol. str. Symbols for which the criteria will be asses
    :param locate_stock_fn. callable. Function filter the given symbol
    :return: Tuple of dicts.
    """
    df_stock = locate_stock_fn(df, symbol)
    if df_stock.isna().sum().sum() != 0:
        return None
    buy_criteria = BuyCriteria(df_stock)
    buy_dict = buy_criteria.run_criteria()
    buy_dict['symbol'] = symbol
    #sell_dict = sell_criteria(df_stock)
    return buy_dict  # sell_dict


def _validate_end_date(end_date):
    """
    Validates given end date corresponds to a business day.

    :param end_date. str or Timestamp.
    """
    if end_date is None:
        today = pd.Timestamp('today')
        if np.is_busday(today.strftime('%Y-%m-%d')):
            return today
        previous_bday = today - pd.tseries.offsets.BDay(1)
        return previous_bday.strftime('%Y-%m-%d')
    assert np.is_busday(end_date), 'Given end date is not a business day'
    return end_date



