from sklearn.linear_model import LinearRegression
import numpy as np


def detect_uptrend(df, column, n_coefs=20, degrees_param=45):
    """
    Determines if an uptrend is present by computing several linear regressions
    on the data. The first linear regressions will gather the last 2 values,
    next the last 3, next for the last 4 and so on.
    That is, the i-th linear regression will consist of the last i+1 points.
    Once the n linear regression are computed and every coefficient (slope) is
    available, an uptrend is said to be present if all coefficients are
    positive.

    Parameters
    ----------
    df: pd.DataFrame.
        Dataframe containing a date column indicating the timestamp of each
        row.

    date_col: str
        Date column

    column: str.
        Column for which the uptrend will be detected.

    n: int.
        Number of coefficients to compute
    """
    print(degrees_param)
    df.reset_index(inplace=True)  # Index column is available from now on
    df_tail_n = df.tail(n_coefs + 1)
    coef_list = _iterative_ols(df_tail_n, ['index'], [column])
    coef_list = np.squeeze(np.concatenate(coef_list))
    return _is_uptrend(coef_list, degrees_param)


def _is_uptrend(coef_list, degrees_param):
    mean_coefs = np.mean(coef_list)
    deg = (np.arctan(mean_coefs) * 180) / np.pi
    if all(coef > 0 for coef in coef_list) and deg >= degrees_param:
        return 1
    return 0


def _iterative_ols(df, x_columns, y_column, reversed_order=True):
    if reversed_order:
        df = df.iloc[::-1].copy()
    coef_list = []
    for n in range(2, len(df) + 1):
        df_head_n = df.head(n)
        _, coef = _ols_from_df(df_head_n, x_columns, y_column)
        coef_list.append(coef)
    return coef_list


def _ols_from_df(df, x_columns, y_column):
    x = df[x_columns].values
    y = df[y_column].values
    model = LinearRegression()
    model.fit(x, y)
    coef = model.coef_
    inter = model.intercept_
    return inter, coef
