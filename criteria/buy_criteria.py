from utils.assertions import *
from trend_detectors.iterative_regression import detect_uptrend
from criteria._criteria import Criteria
import inspect
import sys

BUY_CRITERIA = inspect.getmembers(sys.modules[__name__], inspect.isclass)


class FortyMaUptrend(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._assert_uptrend()

    def _assert_uptrend(self):
        df_40ma = Criteria.compute_ma(self.df, 40)
        uptrend = detect_uptrend(df_40ma, '40ma')
        return uptrend


class TwentyMaUptrend(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._twenty_ma_uptrend()

    def _twenty_ma_uptrend(self):
        df_20ma = Criteria.compute_ma(self.df, 20)
        uptrend = detect_uptrend(df_20ma, '20ma')
        return uptrend


class ContiguousDescHigh(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._contiguous_desc_high()

    def _contiguous_desc_high(self, n=3):
        assert_columns(self.df, 'High')
        df_last_n = self.df.tail(n)
        last_n_high_values = df_last_n['High'].values.tolist()
        if last_n_high_values == sorted(last_n_high_values, reverse=True):
            return 1
        return 0


class ContiguousRedCandles(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan(self):
        return self._contiguous_red_candles()

    def _contiguous_red_candles(self, n=3):
        assert_columns(self.df, ['Open', 'Close'])
        df_last_n = self.df.tail(n)
        last_n_open_minus_close = df_last_n['Open'] - df_last_n['Close']
        if all(last_n_open_minus_close > 0):
            return 1
        return 0

    # def _cambio_guardia(self):
    #     cog = (self.df['Open'].tail(4) - self.df['Close'].tail(4)).values
    #     if all(x > 0 for x in cog[:-1]) and cog[-1] < 0:
    #         return 1
    #     return 0
    #
    # def _cola_piso(self):
    #     assert_columns(df, ['Close', 'Low'])
    #     avg_cdp = (df['Close'] - df['Low']).mean()
    #     df_last = df.tail(1)
    #     close_last = df_last['Close'].item()
    #     low_last = df_last['Low'].item()
    #     cola_de_piso = close_last - low_last
    #     if cola_de_piso > 2 * avg_cdp:
    #         return 1
    #     return 0
