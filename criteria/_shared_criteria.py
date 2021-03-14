from criteria._criteria import Criteria


class SharedCriteria(Criteria):
    def __init__(self, df):
        super().__init__(df)

    def run_criteria(self):
        shared_dict = {'pro volume': self._pro_volume(),
                       'narrow body': self._narrow_body()
                       }
        return shared_dict

    def _pro_volume(self):
        """
        """
        avg_volume = self.df.Volume.mean()
        last_volume = self.df.Volume.tail(1).item()
        if last_volume > avg_volume:
            return 1
        return 0

    def _narrow_body(self):
        """
        """
        avg_body = (abs(self.df.Close - self.df.Open)).mean()
        df_last = self.df.tail(1)
        last_body = abs(df_last.Close.item() - df_last.Open.item())
        if last_body < avg_body:
            return 1
        return 0

    # def pz(df, close_last, open_last):
    #     """
    #     Test de Pristine Zone: El precio de cierre o de apertura de la accion se encuentra entre el 20ma y el 40ma.
    #     """
    #     df_last = df.tail(1)
    #
    #     if (df_last['40ma'].item() < close_last < df_last['20ma'].iloc[-1]) or (open_last > df['40ma'].iloc[-1] and close_last < df['20ma'].iloc[-1]):
    #         return 1
    #     else:
    #         return 0