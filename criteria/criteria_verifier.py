from sources.load_data import load_data
from utils.criteria_utils import dicts_to_dataframe
from criteria._buy_criteria import buy_criteria
from criteria._sell_criteria import sell_criteria
import numpy as np
import pandas as pd


def criteria_verifier(stocks, end_date=None, source='yahoo', params=None):
    """
    Verifies buy and sell criteria for each given stock.
    The time period used consists of 40 busy days and is defined wrt to the given end_date.

    :param stocks: list. Collection of stocks.
    :param end_date: str. Date on which the verification process will take place. If None today's date will be used.
    :param source: str. Source identifier from which stocks data will be obtained. If None, yahoo source will be used.
    :param params: dict. Params from criteria. If None, default params are used.
    :return:
    """
    end_date = _validate_end_date(end_date)
    params = _validate_params(params)
    df, locate_stock_fn = load_data(stocks, end_date, source)
    buy_options, sell_options = dict(), dict()
    for s in stocks:
        df_stock = locate_stock_fn(df, s)
        if df_stock.isna().sum().sum() != 0:
            continue
        buy_criteria_for_stock, sell_criteria_for_stock = _run_criteria_for_stock(df_stock, params)
        buy_options[s] = buy_criteria_for_stock
        sell_options[s] = sell_criteria_for_stock
    dfs = dicts_to_dataframe((buy_options, sell_options))
    return dfs


def _run_criteria_for_stock(df_stock, params):
    """
    Runs buy and sell criteria for the given stock data
    :param df_stock: pd.DataFrame. Dataframe containing the stock data
    :param params: dict. Dictionary containing the criteria parameters
    :return: Tuple of dicts.
    """
    buy_criteria_dict = buy_criteria(df_stock, **params)
    sell_criteria_dict = sell_criteria(df_stock, **params)
    return buy_criteria_dict, sell_criteria_dict


def _validate_end_date(end_date):
    """
    Validates given end date corresponds to a business day
    """
    if end_date is None:
        today = pd.Timestamp('today')
        if np.is_busday(today.strftime('%Y-%m-%d')):
            return today
        else:
            previous_bday = today - pd.tseries.offsets.BDay(1)
            return previous_bday.strftime('%Y-%m-%d')
    else:
        assert np.is_busday(end_date), 'Given end date is not a business day'
        return end_date


def _validate_params(params):
    """
    Validates every criteria param is included

    :param params: dict. Dictionary contraining the criteria parameters
    """
    if params is None:
        params = _get_default_params()
        return params
    else:
        needed_params = ['pbs', 'cola', 'nrb', 'vol']
        for param in needed_params:
            assert param in params, f'Param {param} not found in given params'


def _get_default_params():
    """
    Defines default criteria parameters
    :return: dict. Dictionary containing the default criteria parameters
    """
    default_params = {'pbs': 0.02, 'cola': 2, 'nrb': 0.4, 'vol': 1.5}
    return default_params




