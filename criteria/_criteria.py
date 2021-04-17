from abc import ABCMeta, abstractmethod


class Criteria(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, df):
        self.df = df

    @abstractmethod
    def scan(self):
        pass

    @staticmethod
    def compute_ma(df, n, on='Close'):
        """
        Computes the n moving average on the given column.
        """
        df_ma = df.sort_values('Date')[['Date']].copy()
        df_ma[f'{n}ma'] = df[on].rolling(n).mean()
        df_ma.columns.name = None
        return df_ma
