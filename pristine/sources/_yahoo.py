import pandas_datareader.data as web
import pandas as pd


def yahoo_source(symbols, start_date, end_date):
    df_source = web.DataReader(symbols, 'yahoo', start_date, end_date)
    df_source = df_source.swaplevel(0, 1, 1)
    df_source = _clean_df_source(df_source, symbols)
    _clean_cols(df_source)
    return df_source


def _clean_df_source(df_source, symbols):
    dfs = []
    for sym in symbols:
        df_sym = df_source.loc[:, sym].copy()
        df_sym.loc[:, 'Symbol'] = sym
        dfs.append(df_sym)
    df_source = pd.concat(dfs).reset_index()
    df_source.dropna(inplace=True)
    _drop_zero_volume(df_source)
    return df_source


def _clean_cols(df_source):
    df_source.columns = df_source.columns.str.replace(' ', '_')
    df_source.columns = map(str.lower, df_source.columns)


def _drop_zero_volume(df_source):
    drop_idx = df_source.loc[df_source['Volume'] == 0].index
    df_source.drop(drop_idx, inplace=True)
