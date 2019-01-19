import time
from typing import Dict
from collections import deque
import numpy as np
#from kalman import KalmanFilter


class Plane(object):

    def __init__(self, reg: str, attr: Dict):
        self.Reg = reg
        self.__dict__.update(attr)
        self.last_seen = time.time()
        self.set_colour()
        self.reported_track = deque([], maxlen=3) # used to calculate position
        self.track = deque([], maxlen=3) # used to store track
        #self.kalman_filter = KalmanFilter(1e-4, .04**2) # measured .04 stddev

    def set_colour(self):
        if not self.Type:
            self.colour = (.15, .3)
            return
        if self.Type.startswith("A38"):
            self.colour = (0., .99)
        elif self.Type.startswith("B74"):
            self.colour = (.1, .95)
        elif self.Type.startswith("B77"):
            self.colour = (.63, .99)
        elif self.Type.startswith("B78"):
            self.colour = (.63, .99)
        elif self.Type.startswith("B73"):
            self.colour = (.36, .55)
        elif self.Type.startswith("A32"):
            self.colour = (.36, .55)
        elif self.Type.startswith("A31"):
            self.colour = (.36, .55)
        elif self.Type.startswith("A33"):
            self.colour = (.49, .32)
        elif self.Type.startswith("A34"):
            self.colour = (.49, .32)
        elif self.Type == "static":
            self.colour = (.01, .99)
        else:
            self.colour = (.15, .3)

    def update_fields(self, ac: Dict):
        ac = {k: v for k, v in ac.items() if v is not None}
        self.__dict__.update(ac)
        #self.apply_k_filter()
        self.reported_track.append((self.Lat, self.Long))
        self.Lat = np.mean([coord[0] for coord in self.reported_track])
        self.Long = np.mean([coord[1] for coord in self.reported_track])
        self.track.append((self.Lat, self.Long))
        self.last_seen = time.time()

    def apply_k_filter(self):
        self.kalman_filter.input_measurement((self.Lat, self.Long))
        self.kLat, self.kLong = self.kalman_filter.get_estimated_position()

    @staticmethod
    def extract_data(ac: Dict) -> Dict:
        keys = ("Lat", "Long", "From", "To", "Type", "Alt", "Mdl", "Op")
        data = {k: ac.get(k) for k in keys}
        #data["kLat"], data["kLong"] = ac.get("Lat"), ac.get("Long")
        return data
