from abc import ABCMeta, abstractmethod
from criteria._shared_criteria import SharedCriteria


class Criteria(metaclass=ABCMeta):

    def __init__(self, df):
        self.df = df

    @abstractmethod
    def run_criteria(self):
        """
        Verifies which criteria is accomplished for the given stock data.
        A dictionary is constructed with keys being the criteria name and values either a 1 or 0 indicating if the criteria was met.
        Example:
            Let n the number of criteria for some criteria type, say buy. Then, this method must construct a dictionary of the form
            buy_criteria_ = {'criteria_0': 0, 'criteria_1': 1, ..., 'criteria_n-1: 0'}
        """
        pass

    def compute_ma(self, column, n):
        df_ma = self.df.sort_values('Date')[['Date']].copy()
        df_ma[f'{n}ma'] = self.df[column].rolling(n).mean()
        df_ma.columns.name = None
        return df_ma

    def add_shared_criteria(self, criteria):
        shared_criteria = SharedCriteria(self.df)
        shared_dict = shared_criteria.run_criteria()
        return {**criteria, **shared_dict}
