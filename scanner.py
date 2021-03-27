from sources.load_data import load_data
from criteria.buy_criteria import BUY_CRITERIA
from criteria.common_criteria import COMMON_CRITERIA
import numpy as np
import pandas as pd


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
        self.locate_fn = load_data(symbols, end_date)

    def scan(self):
        """
        Scans pristine criteria for all symbols.
        """
        buy_results = []
        sell_results = []
        for sym in self.symbols:
            buy_scan, sell_scan = self._sym_scanning(sym)
            buy_results.append(buy_scan)
            sell_results.append(sell_scan)
        df_buy = pd.DataFrame(buy_results)
        df_sell = pd.DataFrame(sell_results)
        return df_buy, df_sell

    def _sym_scanning(self, sym):
        df_sym = self.locate_fn(sym)
        sell_scan = {}
        buy_scan = self._scan_buy_criteria(df_sym)
        common_scan = self._scan_common_criteria(df_sym)
        buy_scan = {**buy_scan, **common_scan, 'symbol': sym}
        return buy_scan, sell_scan

    def _scan_buy_criteria(self, df):
        scan_results = {}
        for cls in BUY_CRITERIA:
            scan_results[cls.name] = cls(df).scan()
        return scan_results

    def _scan_common_criteria(self, df):
        scan_results = {}
        for cls in COMMON_CRITERIA:
            scan_results[cls.name] = cls(df).scan()
        return scan_results

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

