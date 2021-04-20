from criteria._criteria import Criteria


class SellCriteria(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def scan_criteria(self):
        """
        """

        sell_dict = {}
        return sell_dict

    # def _cambio_guardia(self, df):
    #     """
    #     """
    #     cog = (df['Open'].tail(4) - df['Close'].tail(4)).values
    #     if all(x < 0 for x in cog[:-1]) and cog[-1] > 0:
    #         return 1
    #     else:
    #         return 0
    #
    # def _cola_techo(self, df):
    #     """
    #     """
    #     avg_cdt = (df['High'] - df[
    #         'Open']).mean()  ## considerar promediar exclusivamente las (40? 100?) muestras mas recientes
    #     cola_de_techo = high_last - open_last
    #     if cola_de_techo > cola_param * avg_cdt:
    #         return 1
    #     else:
    #         return 0
