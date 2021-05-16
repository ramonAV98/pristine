import pandas as pd
import numpy as np
from ._yahoo import yahoo_source

SECTOR_DF_PATH = 'csv/sect_df.csv'
FINANCIAL_COLS = ['symbol', 'adj_close', 'close', 'high', 'low', 'open',
                  'volume']


class Datasource:
    def __init__(self, symbols, end_date, start_date=None, source='yahoo'):
        self.symbols = symbols
        self.end_date = end_date
        self._validate_end_date()
        self.start_date = (start_date if start_date is not None
                           else self._find_start_end())
        self.source = source

    def load(self):
        """
        :param symbols:
        :param end_date:
        :param source:
        :return:
        """
        if self.source == 'yahoo':
            df_source = yahoo_source(self.symbols, self.start_date,
                                     self.end_date)
        else:
            raise ValueError(f"Source '{self.source}' not available")

        self._validate_financial_cols(df_source)
        df_source = self._merge_sector(df_source)
        return df_source

    def _validate_financial_cols(self, df):
        for col in FINANCIAL_COLS:
            assert col in df, f'Financial column "{col}" not found.'

    def _merge_sector(self, df):
        df_sector = pd.read_csv(SECTOR_DF_PATH, header=0, index_col=0)
        df_sector.dropna(inplace=True)
        df_merge = pd.merge(df, df_sector, on='symbol', how='inner')
        return df_merge

    def _find_start_end(self):
        # TODO: load exactly 80 days.
        bdate_range = pd.bdate_range(end=self.end_date, periods=100)
        start_date = bdate_range[0].strftime('%Y-%m-%d')
        return start_date

    def _validate_end_date(self):
        """
        Validates self.end_date corresponds to a business day.
        """
        assert np.is_busday(pd.Timestamp(self.end_date).strftime('%Y-%m-%d'))
