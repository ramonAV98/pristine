from abc import ABCMeta, abstractmethod
from utils.assertions import *


class Criteria(metaclass=ABCMeta):

    def __init__(self, df):
        self.df = df

    @abstractmethod
    def run_criteria(self):
        """
        Verifies which criteria is accomplished for the given stock data.
        A dictionary is constructed with keys being the criteria name and values either a 1 or 0 indicating if the criteria was met.

        In particular, let n be the number of criteria for some criteria type, say buy.
        Then, this method must construct a dictionary buy_criteria of the form buy_criteria = {'criteria_0': 0, ..., 'criteria_n-1: 0'},
        which includes the buying criteria and the shared criteria (see shared_criteria method inside this class).
        Same applies for sell or any future set of criteria.
        """
        pass

    def compute_ma(self, n, column='Close'):
        """
        Computes the n moving average on the given column.
        """
        assert_columns(self.df, [column, 'Date'])
        df_ma = self.df.sort_values('Date')[['Date']].copy()
        df_ma[f'{n}ma'] = self.df[column].rolling(n).mean()
        df_ma.columns.name = None
        return df_ma

    def shared_criteria(self):
        """
        The following are criteria we are interested in regardless we are buying or selling:
            1. Pro volume
            2. Narrow body
            3. Pristine zone
        This method collects them through a dictionary and makes them available for any derived class.
        """
        shared_criteria = {'pro volume': self._pro_volume(),
                           'narrow body': self._narrow_body(),
                           'pristine zone': self._pristine_zone()}
        return shared_criteria

    def _pro_volume(self):
        assert_columns(self.df, 'Volume')
        avg_volume = self.df['Volume'].mean()
        last_volume = self.df['Volume'].tail(1).item()
        if last_volume > avg_volume:
            return 1
        return 0

    def _narrow_body(self):
        assert_columns(self.df, ['Close', 'Open'])
        avg_body = (abs(self.df['Close'] - self.df['Open'])).mean()
        df_last = self.df.tail(1)
        last_body = abs(df_last.Close.item() - df_last.Open.item())
        if last_body < avg_body:
            return 1
        return 0

    def _pristine_zone(self):
        last_20ma = self.compute_ma(20).tail(1)
        last_40ma = self.compute_ma(40).tail(1)
        close_last = self.df['Close'].tail(1).item()
        open_last = self.df['Open'].tail(1).item()
        if (last_40ma < close_last < last_20ma) or (last_40ma < open_last < last_20ma):
            return 1
        return 0
