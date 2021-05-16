from .criteria import (FtyMaUptrend, TnyMaUptrend, ContRedCandles,
                       ContDescHigh, ColaDePiso, ProVolume, NarrowBody,
                       PristineZone, SectorTrend)
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
        Needed columns: [date_col, symbol_col, 'adj_close', 'close', 'high',
                        'low', 'open', 'volume']
        The primary key for this dataframe should be the composition of
        'Date' and 'Symbol'. That is, each row is uniquely identified by
        its Date and Symbol.
        Defaults columns for date_col and symbol_col are 'Date' and 'Symbol',
        respectively.

    date. str or timestamp. Default None
        Scanning date.  If None, the scanning date corresponds to the maximum
        date on df_source.

    date_col. str. Default 'date'
        Date column on df_source

    symbol_col. str. Default 'symbol'
        Column containing the tickers
    """

    def __init__(self, df_source, date_col='date', symbol_col='symbol',
                 n_coefs=20, cola_param=2, narrow_param=.5, vol_param=5,
                 degrees_param=45):

        self.df_source = df_source
        self.date_col = date_col
        self.symbol_col = symbol_col
        self._validate_df_source()
        self.symbols = self.df_source[symbol_col].unique().tolist()
        self.date = self.df_source[date_col].max()
        self.sector_trend = SectorTrend(df_source, n_coefs,
                                        degrees_param).scan()
        self._kwargs_params = dict(
            n_coefs=n_coefs,
            cola_param=cola_param,
            narrow_param=narrow_param,
            vol_param=vol_param,
            degrees_param=degrees_param
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
        sector = self._get_sym_sector(df_sym)
        buy_scan = self._scan_criteria(df_sym, BUY_CRITERIA)
        common_scan = self._scan_criteria(df_sym, COMMON_CRITERIA)
        buy_scan = {**buy_scan,
                    **common_scan,
                    'sector_trend': self.sector_trend[sector],
                    'symbol': sym,
                    'date': self.date}
        return buy_scan

    def _get_sym_sector(self, df_sym):
        return df_sym.sector.unique().item()

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
            name = cls.__name__
            scan_results[name] = cls(df, **self._kwargs_params).scan()
        return scan_results
