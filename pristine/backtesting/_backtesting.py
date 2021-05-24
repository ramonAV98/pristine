from ..sources import Datasource
from ..scanner import Scanner
import sys
import pandas as pd


class Backtesting:
    def __init__(self, symbols, end_date, n_days, n_coefs=20, cola_param=2,
                 narrow_param=.5, vol_param=2, symbol_col='symbol',
                 date_col='date'):

        self.symbols = symbols
        self.end_date = end_date
        self.n_days = n_days
        self.symbol_col = symbol_col
        self.date_col = date_col
        self._date_range = self._def_date_range()
        self.start_date = self._date_range.min()
        self.df_source = None
        self.scan_params = dict(
            n_coefs=n_coefs,
            cola_param=cola_param,
            narrow_param=narrow_param,
            vol_param=vol_param,
        )

    def run(self):
        source = Datasource(self.symbols, self.end_date, self.start_date)
        print('Loading data from API.')
        self.df_source = source.load()
        print('Finish loading.')
        df_backtest = self._scan_multiple_dates()
        df_backtest.sort_values(['symbol', 'date'], inplace=True)
        df_backtest.reset_index(drop=True, inplace=True)
        return df_backtest

    def _loc_date(self, date):
        mask = (self.df_source[self.date_col] <= date)
        return self.df_source[mask].copy()

    def _loc_sym(self, sym):
        mask = (self.df_source[self.symbol_col] == sym)
        return self.df_source[mask]

    def _scan_multiple_dates(self):
        dfs = []
        iteration_dates = self._date_range[-self.n_days:]  # Last n days
        for date in Backtesting._progressbar(list(reversed(iteration_dates))):
            df_source_date = self._loc_date(date)
            s = Scanner(df_source_date, **self.scan_params)
            df_date_scan = s.scan()  # Scanning for single date
            dfs.append(df_date_scan)
        return pd.concat(dfs)

    def _def_date_range(self):
        periods = self.n_days + 60
        date_range = pd.bdate_range(end=self.end_date, periods=periods)
        return date_range

    @staticmethod
    def find_buy_options(df):
        # Pristine setup
        uptrends = (df.ftymauptrend == 1) & (df.tnymauptrend == 1)
        red_candles = (df.contredcandles == 1)
        desc_high = (df.contdeschigh == 1)
        setup = ((uptrends & red_candles) | (uptrends & desc_high) |
                 (uptrends & red_candles & desc_high))

        # Rest of criteria
        vol = (df.provolume == 1)
        nb = (df.narrowbody == 1)
        pz = (df.pristinezone == 1)
        cdp = (df.coladepiso == 1)
        cond = ((vol & nb) | (vol & pz) | (vol & cdp) | (nb & pz) | (nb & cdp)
                | (pz & cdp) | (vol & nb & pz) | (vol & pz & cdp) |
                (nb & pz & cdp) | (vol & nb & cdp) | (vol & nb & cdp & pz))

        return df.loc[setup & cond]

    @staticmethod
    def filter_degrees(df, deg_limit):
        mask = ((df.ftymauptrend_deg >= deg_limit) &
                (df.tnymauptrend_deg >= deg_limit))

        return df.loc[mask]

    @staticmethod
    def _progressbar(it, prefix="Scanning: ", size=60, file=sys.stdout):
        count = len(it)

        def show(j):
            x = int(size * j / count)
            file.write("%s[%s%s] %i/%i\r" % (
            prefix, "#" * x, "." * (size - x), j, count))
            file.flush()

        show(0)
        for i, item in enumerate(it):
            yield item
            show(i + 1)
        file.write("\n")
        file.flush()


