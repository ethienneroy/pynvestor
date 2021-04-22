import datetime
from json import JSONEncoder


class Trade(JSONEncoder):
    # [MTS,OPEN,CLOSE,HIGH,LOW,VOLUME]
    def __init__(self, dt):
        super().__init__()
        # self.mts = datetime.datetime.fromtimestamp(dt[0] / 1000)  # epoch time has to be divided by 1000
        self.mts = datetime.datetime.fromtimestamp(dt[0])  # epoch time has to be divided by 1000
        self.open = dt[1]
        self.close = dt[2]
        self.high = dt[3]
        self.low = dt[4]
        self.volume = dt[5]

    def default(self, o):
        return o.__dict__