from .criteria import (FtyMaUptrend, TnyMaUptrend, ContRedCandles,
                       ContDescHigh, ColaDePiso, ProVolume, NarrowBody,
                       PristineZone)
import pandas as pd

BUY_CRITERIA = [
    FtyMaUptrend,
    TnyMaUptrend,
    ContRedCandles,
    ContDescHigh,
    ColaDePiso
]
COMMON_CRITERIA = [
    ProVolume,
    NarrowBody,
    PristineZone
]

FINANCIAL_COLS = [
    'symbol',
    'adj_close',
    'close',
    'high',
    'low',
    'open',
    'volume'
]


class Scanner:
    """
    Pristine scanner.

    Scans the set for buy and sell criteria for the given df_source.

    Parameters
    ----------
    df_source. pd.DataFrame
        Dataframe containing data for all the symbols that want to be scanned.
        The primary key for this dataframe should be the composition
        (date, symbol). That is, each row is uniquely identified by its
        timestamp and symbol.

    date. str or timestamp. Default None
        Scanning date.  If None, the scanning date corresponds to the maximum
        date on df_source.

    date_col. str. Default 'date'
        Date column on df_source

    symbol_col. str. Default 'symbol'
        Column containing the tickers

    Raises
    ------
    AssertionError if any of the following (financial) columns is not present:
    [date_col, symbol_col, 'adj_close', 'close', 'high', 'low', 'open',
    'volume'].
    """

    def __init__(self, df_source, date_col='date', symbol_col='symbol',
                 n_coefs=20, cola_param=2, narrow_param=.5, vol_param=5):

        self.df_source = df_source
        self.date_col = date_col
        self.symbol_col = symbol_col
        self._validate_df_source()
        self.symbols = self.df_source[symbol_col].unique().tolist()
        self.date = self.df_source[date_col].max()
        self._kwargs_params = dict(
            n_coefs=n_coefs,
            cola_param=cola_param,
            narrow_param=narrow_param,
            vol_param=vol_param,
        )

    def _validate_df_source(self):
        primary_cols = [self.date_col, self.symbol_col]
        for col in FINANCIAL_COLS + primary_cols:
            assert col in self.df_source, f'Financial column "{col}" not found'
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
        n_coefs = self._kwargs_params['n_coefs']
        if len(df_sym) < n_coefs + 40:
            return None
        buy_scan = self._scan_criteria(df_sym, BUY_CRITERIA)
        common_scan = self._scan_criteria(df_sym, COMMON_CRITERIA)
        buy_scan = {**buy_scan,
                    **common_scan,
                    'symbol': sym,
                    'date': self.date}
        return buy_scan

    def _loc_sym(self, sym):
        """
        Locate a single symbol in self.df_source
        """
        mask = (self.df_source[self.symbol_col] == sym)
        df_sym = self.df_source.loc[mask]
        return df_sym

    def _scan_criteria(self, df, criteria):
        """
        Calls scan method for each class element inside a criteria collection.
        """
        scan_results = {}
        for cls in criteria:
            name = cls.__name__.lower()
            scan = cls(df, **self._kwargs_params).scan()
            if isinstance(scan, tuple):
                # The only criteria that returns tuples are the ma uptrends.
                # The tuple is of the from (bool, deg) where bool indicates
                # the presence of a uptrend according to the ols_criterion and
                # deg is the slope degrees.
                scan_results[name] = scan[0]
                scan_results[name + '_deg'] = round(scan[1], 3)
            else:
                scan_results[name] = scan
        return scan_results
