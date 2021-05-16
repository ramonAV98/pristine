from pristine.criteria._criteria import Criteria


class ProVolume(Criteria):
    def __init__(self, df, vol_param, **kwargs):
        super().__init__(df)
        self.vol_param = vol_param

    def scan(self):
        return self._pro_volume()

    def _pro_volume(self):
        avg_volume = self.df.volume.mean()
        last_volume = self.df.volume.tail(1).item()
        if last_volume > self.vol_param * avg_volume:
            return 1
        return 0


class NarrowBody(Criteria):
    def __init__(self, df, narrow_param, **kwargs):
        super().__init__(df)
        self.narrow_param = narrow_param

    def scan(self):
        return self._narrow_body()

    def _narrow_body(self):
        avg_body = (abs(self.df.close - self.df.open)).mean()
        df_last = self.df.tail(1)
        last_body = abs(df_last.close.item() - df_last.open.item())
        if last_body < self.narrow_param * avg_body:
            return 1
        return 0


class PristineZone(Criteria):
    def __init__(self, df, **kwargs):
        super().__init__(df)

    def scan(self):
        return self._pristine_zone()

    def _pristine_zone(self):
        last_20ma = Criteria.compute_ma(self.df, 20).tail(1)['20ma'].item()
        last_40ma = Criteria.compute_ma(self.df, 40).tail(1)['40ma'].item()
        close_last = self.df.close.tail(1).item()
        open_last = self.df.open.tail(1).item()
        close_last_pz = last_40ma < close_last < last_20ma
        open_last_pz = last_40ma < open_last < last_20ma
        if close_last_pz or open_last_pz:
            return 1
        return 0
