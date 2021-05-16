import pandas as pd
from pristine.sources import _datasource
from pristine.scanner import Scanner

class Backtesting:
    def __init__(self, symbols, end_date, n_days, symbol_col='Symbol',
                 date_col='Date'):
        self.symbols = symbols
        self.end_date = end_date
        self.n_days = n_days
        self.symbol_col = symbol_col
        self.date_col = date_col
        self.date_range = self._def_date_range()
        self.start_date = self.date_range.min()
        self.df_source = _datasource(self.symbols, end_date, self.start_date)

    def run(self):
        df_scan = self._scan_multiple_dates()
        df_fin = self._add_cols_to_finantial_data()
        merge_cols = [self.symbol_col, self.date_col]
        df_backtest = pd.merge(df_scan, df_fin, on=merge_cols)
        self._add_buy_col(df_backtest)
        dfs = []
        for sym in self.symbols:
            df_sym = df_backtest.loc[df_backtest['Symbol'] == sym]
            self._add_pct_col(df_sym)
            dfs.append(df_sym)
        return pd.concat(dfs)

    def _loc_date(self, date):
        mask = (self.df_source[self.date_col] <= date)
        return self.df_source[mask]

    def _loc_sym(self, sym):
        mask = (self.df_source[self.symbol_col] == sym)
        return self.df_source[mask]

    def _scan_multiple_dates(self):
        dfs = []
        for date in reversed(self.date_range[-self.n_days:]):  # Last n days
            df_source_date = self._loc_date(date)
            s = Scanner(df_source_date)
            df_date_scan = s.scan()  # Scanning for single date
            dfs.append(df_date_scan)
        return pd.concat(dfs)  # Scanning for all dates

    def _add_cols_to_finantial_data(self):
        dfs = []
        for sym in self.symbols:
            df_sym = self._loc_sym(sym)
            self._add_target_col(df_sym)
            self._add_prev_high_col(df_sym)
            dfs.append(df_sym)
        return pd.concat(dfs)


    def _add_buy_col(self, df):
        # Pristine setup
        uptrends = (df['FtyMaUptrend'] == 1) & (df['TnyMaUptrend'] == 1)
        sector = (df['SectorTrend'] == 1)
        prev_high = (df['PrevHigh'] == 1)
        red_candles = (df['ContRedCandles'] == 1)
        desc_high = (df['ContDescHigh'] == 1)
        setup = ((uptrends & red_candles & prev_high & sector) |
                 (uptrends & desc_high & prev_high & sector) |
                 (uptrends & red_candles & desc_high & prev_high & sector))

        # Rest of criteria
        vol = (df['ProVolume'] == 1)
        nb = (df['NarrowBody'] == 1)
        pz = (df['PristineZone'] == 1)
        cdp = (df['ColaDePiso'] == 1)
        cond = ((vol & nb & pz) |
                (vol & pz & cdp) |
                (nb & pz & cdp) |
                (vol & nb & cdp) |
                (vol & nb & cdp & pz))

        # Add column
        df['Buy'] = 0
        df.loc[setup & cond, 'Buy'] = 1

    def _add_target_col(self, df_sym):
        df_sym.reset_index(drop=True, inplace=True)

        # high_t 1.03 veces más alto que high_t-1
        alpha = 1.03
        df_sym['High_t-1'] = df_sym['High'].shift(1)
        cond_high = df_sym['High'] > alpha * df_sym['High_t-1']

        # low_t igual o mayor low_t-1
        df_sym['Low_t-1'] = df_sym['Low'].shift(1)
        cond_low = df_sym['Low'] > df_sym['Low_t-1']

        # locate dates where both conds are True
        df_sym['Target'] = 0
        bool_mask = (cond_high & cond_low)
        df_sym.loc[bool_mask, 'Target'] = 1

        # shift target
        df_sym['Target'] = df_sym['Target'].shift(-1)

    def _add_prev_high_col(self, df_sym):
        df_sym.reset_index(drop=True, inplace=True)

        cond_high = df_sym['High'] > df_sym['High'].shift(1)
        cond_open = df_sym['Open'] < df_sym['High'].shift(1)

        df_sym['PrevHigh'] = 0
        df_sym.loc[(cond_high & cond_open), 'PrevHigh'] = 1

        df_sym['PrevHigh'] = df_sym['PrevHigh'].shift(-1)

    def _add_pct_col(self, df_sym):
        assert 'Target' in df_sym, 'Target column needed'
        assert 'Buy' in df_sym, 'Buy column needed'

        # shifts
        df_sym['High_t-1'] = df_sym['High'].shift(-1)
        df_sym['Low_t-1'] = df_sym['Low'].shift(-1)

        # win scenario
        win_mask = (df_sym['Target'] == 1) & (df_sym['Buy'] == 1)
        df_sym.loc[win_mask, 'Delta pct'] = 3

        # stop loss
        lose_mask = (df_sym['Target'] == 0) & (df_sym['Buy'] == 1)
        stop_loss_mask = (lose_mask & (df_sym['Low'] < df_sym['Low_t-1']))
        df_diff = ((df_sym['Low_t-1'] - df_sym['High_t-1']) / df_sym[
            'High_t-1']) * 100
        df_sym.loc[stop_loss_mask, 'Delta pct'] = df_diff[stop_loss_mask]

        # middle
        df_diff = ((df_sym['Close'] - df_sym['High_t-1']) / df_sym[
            'High_t-1']) * 100
        middle_mask = lose_mask & ~stop_loss_mask
        df_sym.loc[middle_mask, 'Delta pct'] = df_diff[middle_mask]

    def _def_date_range(self):
        periods = self.n_days + 60
        date_range = pd.bdate_range(end=self.end_date, periods=periods)
        return date_range


