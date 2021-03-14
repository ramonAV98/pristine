from utils.assertions import *
from criteria.trend_detectors.iterative_regression import detect_uptrend
from criteria._criteria import Criteria


class BuyCriteria(Criteria):

    def __init__(self, df):
        super().__init__(df)

    def run_criteria(self):
        buy_dict = {'40ma uptrend': self._40ma_uptrend(),
                    '20ma uptrend': self._20ma_uptrend(),
                    'contiguous desc high': self._contiguous_descendant_high(),
                    'contiguous red candles': self._contiguous_red_candles(),
                    }
        buy_dict = self.add_shared_criteria(buy_dict)
        return buy_dict

    def _40ma_uptrend(self):
        assert_columns(self.df, 'Date')
        self.df.sort_values('Date', inplace=True)
        df_40ma = self.compute_ma('Close', 40)
        uptrend = detect_uptrend(df_40ma, '40ma')
        return uptrend

    def _20ma_uptrend(self):
        self.df.reset_index(inplace=True)
        self.df.sort_values('Date', inplace=True)
        df_20ma = self.compute_ma('Close', 20)
        uptrend = detect_uptrend(df_20ma, '20ma')
        return uptrend

    def _contiguous_descendant_high(self, n=3):
        assert_columns(self.df, 'High')
        df_last_n = self.df.tail(n)
        last_n_high_values = df_last_n['High'].values.tolist()
        if last_n_high_values == sorted(last_n_high_values, reverse=True):
            return 1
        return 0

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
