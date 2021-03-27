from sources.load_data import load_data
from criteria.buycriteria import (FtyMaUptrend, TnyMaUptrend, ContRedCandles,
                                  ContDescHigh)
from criteria.cmncriteria import (ProVolume, NarrowBody, PristineZone)
import numpy as np
import pandas as pd

BUY_CRITERIA = [FtyMaUptrend, TnyMaUptrend, ContRedCandles, ContDescHigh]
COMMON_CRITERIA = [ProVolume, NarrowBody, PristineZone]
# SELL_CRITERIA = []


class Scanner:

    def __init__(self, symbols, end_date=None, source='yahoo'):
        """
        Parameters
        ----------
        symbols: list. Collection of stock symbols (i.e., tickers).
        end_date: str. Date on which the verification process will take place.
        If None, defaults to today's date.
        source: str. Source identifier from which stocks data will be obtained.
        If None, defaults to yahoo source.
        """
        self.symbols = symbols
        self.end_date = end_date
        self.source = source
        self._validate_end_date()
        self.locate_fn = load_data(symbols, self.end_date)

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
        df_sym = self.locate_fn(sym)
        if df_sym.isna().sum().sum() != 0:
            return None
        buy_scan = self._scan_criteria_collection(df_sym, BUY_CRITERIA)
        common_scan = self._scan_criteria_collection(df_sym, COMMON_CRITERIA)
        buy_scan = {**buy_scan, **common_scan, 'Symbol': sym}
        return buy_scan

    def _scan_criteria_collection(self, df, collection):
        scan_results = {}
        for cls in collection:
            name = cls.__name__
            scan_results[name] = self._scan_criteria(df, cls)
        return scan_results

    def _scan_criteria(self, df, criteria_cls):
        return criteria_cls(df).scan()

    def _validate_end_date(self):
        """
        Validates given end date corresponds to a business day.
        """
        if self.end_date is None:
            today = pd.Timestamp('today')
            if np.is_busday(today.strftime('%Y-%m-%d')):
                self.end_date = today
            else:
                previous_bday = today - pd.tseries.offsets.BDay(1)
                self.end_date = previous_bday.strftime('%Y-%m-%d')
        else:
            assert np.is_busday(self.end_date), ('Given end date is not a '
                                                 'business day')

