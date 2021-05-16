from abc import ABCMeta, abstractmethod


class Criteria(metaclass=ABCMeta):
    """Base class for all criteria.

    Warning:
        This class should not be used directly. Use derived classes instead.
    """

    @abstractmethod
    def __init__(self, df, **kwargs):
        self.df = df

    @abstractmethod
    def scan(self):
        pass

    @staticmethod
    def compute_ma(df, ma, date_col='date', on='close'):
        """
        Computes the n moving average on the given column.
        """
        df_ma = df.sort_values(date_col)[[date_col]].copy()
        df_ma[f'{ma}ma'] = df[on].rolling(ma).mean()
        df_ma.columns.name = None
        return df_ma
