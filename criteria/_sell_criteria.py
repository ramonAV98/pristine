from utils.criteria_utils import *
import numpy as np


def sell_criteria(df_stock, pbs, cola, nrb, vol):
    """
    Verifies which criterion is accomplished for the given stock data.

    :param df_stock: pd.DataFrame. Dataframe containing data for a single stock
    :param pbs: float. Buy setup param
    :param cola: float. Cola de piso param
    :param nrb: float. Nrb param
    :param vol: float. Pro volume param
    :return: dict. Dictionary with boolean values containing which criteria were accomplished
    """
    high_last, close_last, _, open_last = get_last_values(df_stock)
    pss = -pbs
    sell_criteria_dict = {'setup': _sell_setup(df_stock, pss),
                          'cambio de guardia': _cambio_guardia(df_stock),
                          'cola de techo': _cola_techo(df_stock, cola, high_last, open_last),
                          'narrow body': narrow_body(df_stock, nrb, close_last, open_last),
                          'pz': pz(df_stock, close_last, open_last),
                          'pro volume': pro_volume(df_stock, vol)
                          }
    return sell_criteria_dict


def _sell_setup(df, pss_param):
    """
    Pristine Selling Setup. Indispensable que se cumpla para vender.
    Regresa True si se cumple:
        1. Pristine Selling Setup
        2. 20ma es Bajista
        3. 40ma es Bajista

    Parámetros:
    ------------
    df: pd.DataFrame. Extrae data de yahoo sobre una determinada accion en un periodo de tiempo
    pss_param: float. Parametro que define la pendiente considerada bajista del 20ma y 40ma
    constant_values: dic. Diccionario con las constantesop

    Cambios:
    -----------
    El función recibe ahora constant_values para generar las constantes
    """
    try:  # protege el código de que haya acciones sin el número suficiente de registros para el vector PBS

        pss = list(df['Low'].tail(3))  # las 3 mas recientes de high
        open_last = df['Open'].iloc[-1]
        close_last = df['Close'].iloc[-1]
        close_last_2 = df['Close'].iloc[-2]
        open_last_2 = df['Open'].iloc[-2]
        open_last_3 = df['Open'].iloc[-3]
        close_last_3 = df['Close'].iloc[-3]
        avg_change20ma = (np.diff(normalize(df['20ma'].tail(20)))).mean()
        avg_change40ma = (np.diff(normalize(df['40ma'].tail(40)))).mean()
        # PSS_0 = constant_values.get('low_last')  # ultimo elemento de open (mas reciente)

        # if any(all[],all[])...si cualquiera de los dos all() se cumple pasa
        if any([
            all([
                pss[0:3] == sorted(pss[0:3], reverse=False),
                avg_change20ma < pss_param,
                avg_change40ma < pss_param
            ]),
            all([
                close_last > open_last,
                close_last_2 > open_last_2,
                close_last_3 > open_last_3,
                avg_change20ma < pss_param,
                avg_change40ma < pss_param
            ])
        ]):
            return 1
        else:
            return 0
    except IndexError:
        return 0


def _cambio_guardia(df):
    """
    Test de cambio de guardia.
    Regresa True si se cumple:
    1. 3 o mas velas de un color seguidas por una del color opuesto.

    Parametros:
    ------------
    df = pd.DataFrame. Extrae data de yahoo sobre una determinada accion en un periodo de tiempo

    """
    cog = (df['Open'].tail(4) - df['Close'].tail(4)).values
    if all(x < 0 for x in cog[:-1]) and cog[-1] > 0:
        return 1
    else:
        return 0


def _cola_techo(df, cola_param, high_last, open_last):
    """
    Test de cola de techo.
    Regresa True si se cumple:
    1. El tamano de la cola de la vela del ultimo dia es significativamente mayor que el tamano promedio de las colas de techo
    de la muestra

    Parametros:
    ------------
    df = pd.DataFrame. Extrae data de yahoo sobre una determinada accion en un periodo de tiempo
    cola_param: float. Parametro que define lo que se considera significativamente mayor/menor al tamano promedio.

    """
    avg_cdt = (df['High'] - df[
        'Open']).mean()  ## considerar promediar exclusivamente las (40? 100?) muestras mas recientes
    cola_de_techo = high_last - open_last
    if cola_de_techo > cola_param * avg_cdt:
        return 1
    else:
        return 0
