import pandas as pd

# hola
def normalize(values):
    """
    Regresa los valores normalizados de 0 a 1.

    :param values: pd.Series, np.array. Secuencia con los valores a normalizar
    """
    normalized_values = (values - values.min()) / (values.max() - values.min())
    return normalized_values


def get_last_values(df_stock):
    high_last = df_stock['High'].iloc[-1]
    close_last = df_stock['Close'].iloc[-1]
    low_last = df_stock['Low'].iloc[-1]
    open_last = df_stock['Open'].iloc[-1]
    return high_last, close_last, low_last, open_last


def dicts_to_dataframe(dicts, orient='index'):
    dfs = []
    for d in dicts:
        dfs.append(pd.DataFrame.from_dict(d, orient=orient))
    return tuple(dfs)


# ------------------------------------------------------------------------- #
# The following are criteria functions shared by both settings buy and sell #
# ------------------------------------------------------------------------- #

def narrow_body(df, nrb_param, close_last, open_last):
    """
    Test de narrow range body: El tamano del cuerpo de la vela es significativamente menor al tamaño
    promedio de los cuerpos de la muestra.
    """
    avg_body = (abs(df['Close'] - df['Open'])).mean()
    body_last = close_last - open_last
    if body_last < nrb_param * avg_body:
        return 1
    else:
        return 0


def pz(df, close_last, open_last):
    """
    Test de Pristine Zone: El precio de cierre o de apertura de la accion se encuentra entre el 20ma y el 40ma.
    """
    if (df['40ma'].iloc[-1] < close_last < df['20ma'].iloc[-1]) or (open_last > df['40ma'].iloc[-1] and close_last < df['20ma'].iloc[-1]):
        return 1
    else:
        return 0


def pro_volume(df, vol_param):
    """
    Test de volumen profesional: El volumen de compra/venta del dia en cuestion es significativamente mayor al promedio de la muestra.
    """
    if df['Volume'].tail(1).item() > vol_param * (df['Volume']).mean():
        return 1
    else:
        return 0

