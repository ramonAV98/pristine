from pristine.trend_detectors.iterative_ols import detect_uptrend
from pristine.criteria._criteria import Criteria
import numpy as np


class FtyMaUptrend(Criteria):
    """
    <mini resumen>

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe for a single symbol
    """

    def __init__(self, df, n_coefs, degrees_param, **kwargs):
        super().__init__(df)
        self.n_coefs = n_coefs
        self.degrees_param = degrees_param

    def scan(self):
        return self._fty_ma_uptrend()

    def _fty_ma_uptrend(self):
        ma = 40  # 40 because 40ma
        min_dates = ma + self.n_coefs
        assert len(self.df) >= min_dates, ('Symbol df has less than '
                                           f'{min_dates} dates')
        df_40ma = Criteria.compute_ma(self.df, ma=ma)
        uptrend = detect_uptrend(df_40ma, '40ma', self.n_coefs,
                                 self.degrees_param)
        return uptrend


class TnyMaUptrend(Criteria):
    def __init__(self, df, n_coefs, degrees_param, **kwargs):
        super().__init__(df)
        self.n_coefs = n_coefs
        self.degrees_param = degrees_param

    def scan(self):
        return self._twenty_ma_uptrend()

    def _twenty_ma_uptrend(self):
        ma = 20  # 20 because 20ma
        min_dates = ma + self.n_coefs
        assert len(self.df) >= min_dates, ('Symbol df has less than '
                                           f'{min_dates} dates')
        df_20ma = Criteria.compute_ma(self.df, ma=ma)
        uptrend = detect_uptrend(df_20ma, '20ma', self.n_coefs,
                                 self.degrees_param)
        return uptrend


class ContDescHigh(Criteria):
    def __init__(self, df, **kwargs):
        super().__init__(df)

    def scan(self):
        return self._contiguous_desc_high()

    def _contiguous_desc_high(self):
        df_last_n = self.df.tail(3)  # pristine requires at least 3 contiguous
        last_n_high_values = df_last_n.high.values.tolist()
        if last_n_high_values == sorted(last_n_high_values, reverse=True):
            return 1
        return 0


class ContRedCandles(Criteria):
    def __init__(self, df, **kwargs):
        super().__init__(df)

    def scan(self):
        return self._contiguous_red_candles()

    def _contiguous_red_candles(self):
        df_last_n = self.df.tail(3)  # pristine requires at least 3 contiguous
        last_n_open_minus_close = df_last_n.open - df_last_n.close
        if all(last_n_open_minus_close > 0):
            return 1
        return 0


class ColaDePiso(Criteria):
    def __init__(self, df, cola_param, **kwargs):
        super().__init__(df)
        avg_verde = (abs(self.df.open - self.df.low)).mean()
        avg_roja = (abs(self.df.close - self.df.low)).mean()
        self.avg_cola = (avg_verde + avg_roja) / 2
        self.cola_param = cola_param

    def scan(self):
        return self._cola_de_piso_roja() or self._cola_de_piso_verde()

    def _cola_de_piso_verde(self):
        df_last = self.df.tail(1)
        open = df_last.open.item()
        low = df_last.low.item()
        if (open - low) > self.cola_param * self.avg_cola:
            return 1
        return 0

    def _cola_de_piso_roja(self):
        df_last = self.df.tail(1)
        close = df_last.close.item()
        low = df_last.low.item()
        if (close - low) > self.cola_param * self.avg_cola:
            return 1
        return 0


class SectorTrend(Criteria):
    def __init__(self, df, n_coefs, degrees_param, **kwargs):
        super().__init__(df)
        self._sectors = df.sector.unique().tolist()
        self.n_coefs = n_coefs
        self.degrees_param = degrees_param

    def scan(self):
        return self._sector_trend()

    def _wm_fn(self):
        return lambda x: np.average(x, weights=self.df.loc[x.index, 'volume'])

    def _sector_trend(self):
        wm_fn = self._wm_fn()
        groupby_cols = ['sector', 'date']
        agg = {'close': wm_fn}
        df_agg = self.df.groupby(groupby_cols).agg(agg)
        df_agg.reset_index(inplace=True)
        uptrend_by_sector = {}
        for sect in self._sectors:
            mask = df_agg.sector == sect
            df_sect = df_agg.loc[mask].copy()
            if len(df_sect) < self.n_coefs + 40:
                continue
            uptrend = FtyMaUptrend(df_sect, self.n_coefs,
                                   self.degrees_param).scan()
            uptrend_by_sector[sect] = uptrend
        return uptrend_by_sector
