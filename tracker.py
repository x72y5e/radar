import requests
import json
import time
from datetime import datetime
import numpy as np
from typing import Dict
from plane import Plane


try:
    import unicornhathd as u

except ModuleNotFoundError:
    print("No unicorn hat found. Printing to console only.")
    u = 0


def plot(grid: np.ndarray):
    if not u:
        return
    u.clear()
    for x, y in zip(*np.where(grid[:, :, 2] > 0.)):
        u.set_pixel_hsv(x, y, *grid[x, y])
    u.show()


def log(planes: Dict[str, Plane]):
    t = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    data = [" ".join((str(p.kLat), str(p.kLong), str(p.colour))) for p in planes.values()]
    with open("log.txt", "a") as f:
        f.write(t + " - " + " - ".join(data) + "\n")


def make_grid(planes: Dict[str, Plane], grid: np.ndarray,
              x_low, x_high, y_low, y_high) -> np.ndarray:
    grid[:, :, 2] /= 1.8
    grid[grid[:, :, 2] < .1] = 0.
    for plane in planes.values():
        lat, long = plane.kLat, plane.kLong
        h, s = plane.colour
        if not (x_low < lat < x_high and y_low < long < y_high):
            continue
        lat = int(((lat - x_low) / (x_high - x_low)) * -16. + 16)
        long = int(((long - y_low) / (y_high - y_low)) * 16.)
        grid[lat, long] = (h, s, 1.) if plane.Type != "static" else (h, s, 0.1)
    return grid


def purge(planes: Dict[str, Plane]) -> Dict[str, Plane]:
    return {reg: plane for reg, plane in planes.items()
            if (time.time() - plane.last_seen < 45.
                or plane.Type == "static")}


def display_to_console(current_ac: Dict[str, Plane]) -> None:
    # current_ac is a dict in form {registration: Plane()}
    for p in [p for p in current_ac.values() if p.Type != "static"]:
        print("From:", p.From)
        print("To:", p.To)
        print("Type:", p.Type)
        print("Altitude:", p.Alt)
        print("Last Info:", round(time.time() - p.last_seen, 2), "seconds ago")
        print()


def track(lat: float, long: float,
          lat_min: float, lat_max: float, long_min: float, long_max: float,
          r: float = 25.):
    """
    :param lat: latitude of centre of tracking space
    :param long: longitude of centre of tracking space
    :param r: range (km) of tracking, from centre
    :param lat_min: minimum latitude to use for display grid
    :param lat_max: maximum latitude to use for display grid
    :param long_min: minimum longitude to use for display grid
    :param long_max: maximum longitude to use for display grid
    :return: None
    """
    url = "http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat={}&lng={}&fDstL=0&fDstU={}".format(
        lat, long, r)
    current_ac = {}
    # add fixed point(s)
    home = Plane("home", {"Lat": lat, "Long": long, "kLat": lat, "kLong": long,
                          "Type": "static"})

    current_ac["home"] = home
    grid = np.zeros((16, 16, 3))

    while True:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            assert r.ok
            data = json.loads(r.text)
        except:
            print("{}: connection error.".format(datetime.strftime(datetime.now(), "%H:%M:%S")))
            time.sleep(2)
            continue

        for ac in data["acList"]:
            reg = ac.get("Reg")
            core_data = Plane.extract_data(ac)
            if reg:
                plane = current_ac.get(reg)
                if plane:
                    plane.update_fields(core_data)
                else:
                    plane = Plane(reg, core_data)
                    current_ac[reg] = plane

        display_to_console(current_ac)
        current_ac = purge(current_ac)
        grid = make_grid(current_ac, grid, lat_min, lat_max, long_min, long_max)
        plot(grid)
        log(current_ac)
        time.sleep(3)


if __name__ == '__main__':
    home_coords = (51.47, -0.45)
    screen_coords = (51.41, 51.53, -.7, -.24)
    track(*home_coords, *screen_coords, 18.)
