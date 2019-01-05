import time
import numpy as np
from collections import deque
from typing import Dict


class Plane(object):

    def __init__(self, reg: str, attr: Dict) -> None:
        self.Reg = reg
        self.__dict__.update(attr)
        self.track = deque([], maxlen=5)
        self.last_seen = time.time()
        self.set_colour()

    def set_colour(self):
        if self.Type.startswith("A38"):
            self.colour = (0., .99)
        elif self.Type.startswith("B74"):
            self.colour = (0., .99)
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

    def update_fields(self, ac: Dict) -> None:
        ac = {k: v for k, v in ac.items() if not v is None}
        self.__dict__.update(ac)
        # resets lat and long to most recently reported position
        if self.Lat and self.Long:
            # stores most recently reported position
            self.track.append((self.Lat, self.Long))
        if len(self.track) > 1:
            # resets lat and long to average of recent values
            self.Lat = np.mean([pos[0] for pos in self.track])
            self.Long = np.mean([pos[1] for pos in self.track])
        self.last_seen = time.time()

    @staticmethod
    def extract_data(ac: Dict) -> Dict:
        keys = ("Lat", "Long", "From", "To", "Type", "Alt")
        data = {k: ac.get(k) for k in keys}
        return data
