from sources.load_data import load_data
from criteria.buycriteria import (FtyMaUptrend, TnyMaUptrend, ContRedCandles,
                                  ContDescHigh, ColaDePiso)
from criteria.cmncriteria import (ProVolume, NarrowBody, PristineZone)
import numpy as np
import pandas as pd

BUY_CRITERIA = [FtyMaUptrend, TnyMaUptrend, ContRedCandles, ContDescHigh, ColaDePiso]
COMMON_CRITERIA = [ProVolume, NarrowBody, PristineZone]
# SELL_CRITERIA = []


class Scanner:
    """
    Pristine scanner.

    Scans the set for buy and sell criteria for the given df_source.

    Parameters
    ----------
    df_source. pd.DataFrame
        Dataframe containing data for all the symbols that want to be scanned.
        Needed columns: [date_col, symbol_col, 'Adj Close', 'Close', 'High',
                        'Low', 'Open', 'Volume']
        The primary key for this dataframe should be the composition of
        'Date' and 'Symbol'. That is, each row is uniquely identified by
        its Date and Symbol.
        Defaults columns for date_col and symbol_col are 'Date' and 'Symbol',
        respectively.

    date. str or timestamp. Default None
        Scanning date.  If None, the scanning date corresponds to the maximum
        date on df_source.

    date_col. str. Default 'Date'
        Date column on df_source

    symbol_col. str. Default 'Symbol'
        Column containing the tickers
    """

    def __init__(self, df_source, date_col='Date', symbol_col='Symbol'):

        self.df_source = df_source
        self.date_col = date_col
        self.symbol_col = symbol_col
        self._validate_df_source()
        self.symbols = self.df_source[symbol_col].unique().tolist()
        self._date = self.df_source[date_col].max()

    def _validate_df_source(self):
        primary_cols = [self.date_col, self.symbol_col]
        financial_cols = ['Adj Close', 'Close', 'High', 'Low', 'Open',
                          'Volume']
        needed_cols = primary_cols + financial_cols
        for col in needed_cols:
            assert col in self.df_source, f'Column {col} not found'
        unique_dates = self.df_source[self.date_col].unique()
        len_dates = len(unique_dates)
        assert len_dates >= 60, (f'At least 60 dates must be included. Instead'
                                 f' got {len_dates}')
        self.df_source.sort_values([self.date_col, self.symbol_col],
                                   inplace=True)
        self.df_source.reset_index(inplace=True, drop=True)

    def scan(self):
        """
        Scans pristine criteria for all symbols.
        """
        buy_results = []
        for sym in self.symbols:
            scanning = self._scan_sym(sym)
            if scanning is None:
                continue
            buy_results.append(scanning)
        df_buy = pd.DataFrame(buy_results)
        return df_buy

    def _scan_sym(self, sym):
        """
        Scans a single symbol
        """
        df_sym = self._loc_sym(sym)
        buy_scan = self._scan_criteria(df_sym, BUY_CRITERIA)
        common_scan = self._scan_criteria(df_sym, COMMON_CRITERIA)
        buy_scan = {**buy_scan, **common_scan, 'Symbol': sym,
                    'Date': self._date}
        return buy_scan

    def _loc_sym(self, sym):
        """
        Locate a single symbol in self.df_source
        """
        df_sym = self.df_source.loc[self.df_source[self.symbol_col] == sym]
        return df_sym

    def _scan_criteria(self, df, criteria):
        """
        Calls scan method for each element of a criteria collection
        """
        scan_results = {}
        for cls in criteria:
            name = cls.__name__
            scan_results[name] = cls(df).scan()
        return scan_results
