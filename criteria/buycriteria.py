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