import time
from typing import Dict
from collections import deque
import numpy as np
#from kalman import KalmanFilter


class Plane(object):

    def __init__(self, reg: str, attr: Dict):
        self.reg = reg
        # replace "from" key with "frm"
        attr = {(k if not k == "from" else "frm"): v
                for k, v in attr.items()}
        self.__dict__.update(attr)
        self.last_seen = time.time()
        self.set_colour()
        self.reported_track = deque([], maxlen=3) # used to calculate position
        self.track = deque([], maxlen=3) # used to store track
        #self.kalman_filter = KalmanFilter(1e-4, .04**2) # measured .04 stddev

    def set_colour(self):
        if not self.type:
            self.colour = (.15, .3)
            return
        if self.type.startswith("A38"):
            self.colour = (0., .99)
        elif self.type.startswith("B74"):
            self.colour = (.933, .974)
        elif self.type.startswith("B77"):
            self.colour = (.63, .99)
        elif self.type.startswith("B78"):
            self.colour = (.57, .94)
        elif self.type.startswith("B73"):
            self.colour = (.37, .89)
        elif self.type.startswith("A32") or self.type.startswith("A31"):
            self.colour = (.79, .12)
        elif self.type.startswith("A33"):
            self.colour = (.495, .198)
        elif self.type.startswith("A34"):
            self.colour = (.35, .96)
        elif self.type == "static":
            self.colour = (.01, .99)
        #elif self.Type == "":
        else:
            self.colour = (.15, .3)

    def update_fields(self, ac: Dict):
        ac = {k: v for k, v in ac.items() if v is not None}
        self.__dict__.update(ac)
        #self.apply_k_filter()
        self.reported_track.append((self.lat, self.long))
        self.lat = np.mean([coord[0] for coord in self.reported_track])
        self.long = np.mean([coord[1] for coord in self.reported_track])
        self.track.append((self.lat, self.long))
        self.last_seen = time.time()

    def apply_k_filter(self):
        self.kalman_filter.input_measurement((self.Lat, self.Long))
        self.kLat, self.kLong = self.kalman_filter.get_estimated_position()

    @staticmethod
    def extract_data(ac: Dict) -> Dict:
        keys = ("lat", "long", "from", "to", "type", "alt", "mdl", "op")
        data = {k: ac.get(k) for k in keys}
        #data["kLat"], data["kLong"] = ac.get("Lat"), ac.get("Long")
        return data
