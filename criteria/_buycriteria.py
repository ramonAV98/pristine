from trend_detectors.iterative_regression import detect_uptrend
from criteria._criteria import Criteria


class FtyMaUptrend(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._assert_uptrend()

    def _assert_uptrend(self):
        df_40ma = Criteria.compute_ma(self.df, 40)
        uptrend = detect_uptrend(df_40ma, '40ma')
        return uptrend


class TnyMaUptrend(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._twenty_ma_uptrend()

    def _twenty_ma_uptrend(self):
        df_20ma = Criteria.compute_ma(self.df, 20)
        uptrend = detect_uptrend(df_20ma, '20ma')
        return uptrend


class ContDescHigh(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._contiguous_desc_high()

    def _contiguous_desc_high(self, n=3):
        df_last_n = self.df.tail(n)
        last_n_high_values = df_last_n['High'].values.tolist()
        if last_n_high_values == sorted(last_n_high_values, reverse=True):
            return 1
        return 0


class ContRedCandles(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._contiguous_red_candles()

    def _contiguous_red_candles(self, n=3):
        df_last_n = self.df.tail(n)
        last_n_open_minus_close = df_last_n['Open'] - df_last_n['Close']
        if all(last_n_open_minus_close > 0):
            return 1
        return 0


class ColaDePiso(Criteria):
    def __init__(self, df):
        super().__init__(df)
        avg_verde = (abs(self.df['Open'] - self.df['Low'])).mean()
        avg_roja = (abs(self.df['Close'] - self.df['Low'])).mean()
        self.avg_cola = (avg_verde + avg_roja)/2

    def scan(self):
        return self._cola_de_piso_roja() or self._cola_de_piso_verde()

    def _cola_de_piso_verde(self):
        df_last = self.df.tail(1)
        open = df_last['Open'].item()
        low = df_last['Low'].item()
        if (open - low) > 1.5 * self.avg_cola:
            return 1
        return 0

    def _cola_de_piso_roja(self):
        df_last = self.df.tail(1)
        close = df_last['Close'].item()
        low = df_last['Low'].item()
        if (close - low) > 1.5 * self.avg_cola:
            return 1
        return 0


# class SectorTrend(Criteria):
#     def __init__(self, df, sym):
#         super().__init__(df)
#         self.sym = sym
#
#     def scan(self):
#
#
#     def _sector_trend(self):


class Target(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._target()

    def _target(self):
        df_last = self.df.tail(1)
        df_yday = self.df.tail(2)[-2]
        high_today = df_last.High.item()
        high_yday = df_yday.High.item()
        low_today = df_last.Low.item()
        low_yday = df_yday.Low.item()
        if (high_today > (1.03 * high_yday)) & (low_today > low_yday):
            return 1
        return 0
