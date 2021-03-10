from utils.criteria_utils import *
import numpy as np


def buy_criteria(df_stock, pbs, cola, nrb, vol):
    """
    Verifies which criterion is accomplished for the given stock data.

    :param df_stock: pd.DataFrame. Dataframe containing data for a single stock
    :param pbs: float. Buy setup param
    :param cola: float. Cola de piso param
    :param nrb: float. Nrb param
    :param vol: float. Pro volume param
    :return: dict. Dictionary with boolean values containing which criteria were accomplished
    """
    _, close_last, low_last, open_last = get_last_values(df_stock)
    buy_criteria_dict = {'setup': _buy_setup(df_stock, pbs),
                         'cambio de guardia': _cambio_guardia(df_stock),
                         'cola de piso': _cola_piso(df_stock, cola, close_last, low_last),
                         'narrow body': narrow_body(df_stock, nrb, close_last, open_last),
                         'pz': pz(df_stock, close_last, open_last),
                         'pro volume': pro_volume(df_stock, vol)
                         }
    return buy_criteria_dict


def _buy_setup(df, pbs_param):
    """
    Pristine Buying Setup. Indispensable que se cumpla para considerar comprar.
    Dos escenarios son posibles para considerar esta condición como cumplida:
        1.
        2.
    """
    try:  # protege el código de que haya acciones sin el número suficiente de registros para el vector PBS

        pbs = list(df['High'].tail(3))  # las 3 mas recientes de high
        open_last = df['Open'].iloc[-1]
        close_last = df['Close'].iloc[-1]
        close_last_2 = df['Close'].iloc[-2]
        open_last_2 = df['Open'].iloc[-2]
        open_last_3 = df['Open'].iloc[-3]
        close_last_3 = df['Close'].iloc[-3]
        avg_change20ma = (np.diff(normalize(df['20ma'].tail(20)))).mean()
        avg_change40ma = (np.diff(normalize(df['40ma'].tail(40)))).mean()

        # if any(all[],all[])... si cualquiera de los dos all() se cumple
        if any([
            all([
                pbs == sorted(pbs, reverse=True),
                avg_change20ma > pbs_param,
                avg_change40ma > pbs_param
            ]),
            all([
                close_last < open_last,
                close_last_2 < open_last_2,
                close_last_3 < open_last_3,
                avg_change20ma > pbs_param,
                avg_change40ma > pbs_param
            ])
        ]):
            # Esto se tiene que arreglar
            return 1
        else:
            return 0
    except IndexError:
        return 0


def _cambio_guardia(df):
    """
    Test de cambio de guardia: 3 o mas velas de un color seguidas por una del color opuesto.
    """
    cog = (df['Open'].tail(4) - df['Close'].tail(4)).values
    if all(x > 0 for x in cog[:-1]) and cog[-1] < 0:
        return 1
    else:
        return 0


def _cola_piso(df, cola_param, close_last, low_last):
    """
    Test de cola de piso: El tamaño de la cola de la vela del ultimo dia es significativamente mayor
    que el tamano promedio de las colas de piso de la muestra
    """
    avg_cdp = (df['Close'] - df['Low']).mean()
    cola_de_piso = close_last - low_last
    if cola_de_piso > cola_param * avg_cdp:
        return 1
    else:
        return 0
