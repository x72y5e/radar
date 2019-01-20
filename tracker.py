import requests
import json
import time
from datetime import datetime
import numpy as np
from typing import Dict, List, Tuple
import sys
from plane import Plane


try:
    import unicornhathd as u

except ImportError:
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
    data = [" ".join((str(p.Lat), str(p.Long), str(p.colour))) for p in planes.values()]
    with open("log.txt", "a") as f:
        f.write(t + " - " + " - ".join(data) + "\n")


def make_grid(planes: Dict[str, Plane],
              x_low, x_high, y_low, y_high) -> np.ndarray:
    grid = np.zeros((16, 16, 3), dtype=np.float32)
    for plane in planes.values():
        h, s = plane.colour
        if plane.Type == "static":
            x = int(((plane.Lat - x_low) / (x_high - x_low)) * -16. + 16)
            y = int(((plane.Long - y_low) / (y_high - y_low)) * 16.)
            grid[x, y] = (h, s, .1)
        b = 1.
        alt = int(plane.Alt) if plane.Alt is not None else 100
        for x, y in reversed(plane.track):
            if (x_low < x < x_high
                and y_low < y < y_high
                and alt > 50):
                x = int(((x - x_low) / (x_high - x_low)) * -16. + 16)
                y = int(((y - y_low) / (y_high - y_low)) * 16.)
                # get current brightness of pixel to avoid overwriting
                current_b = grid[x, y, 2]
                grid[x, y] = (h, s, max(current_b, b)) if plane.Type != "static" else (h, s, 0.1)
            b /= 2.
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
        print("Type:", p.Mdl) #p.Type)
        print("Operator:", p.Op)
        print("Altitude:", p.Alt)
        print("Last Info:", round(time.time() - p.last_seen, 2), "seconds ago")
        print()


def track(fixed_points: List[Tuple[float, float]],
          lat_min: float, lat_max: float, long_min: float, long_max: float,
          r: float = 25.):
    """
    :param fixed_points: list of fixed points to display. first item is tracking centre
    :param r: range (km) of tracking, from centre
    :param lat_min: minimum latitude to use for display grid
    :param lat_max: maximum latitude to use for display grid
    :param long_min: minimum longitude to use for display grid
    :param long_max: maximum longitude to use for display grid
    :return: None
    """
    lat, long = x_low + (x_high - x_low) / 2, y_low + (y_high - y_low) / 2
    print("getting data...")
    print(lat, long, r)
    url = "https://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat={}&lng={}&fDstL=0&fDstU={}".format(
        lat, long, r)
    current_ac = {}

    # add fixed point(s)
    for i, (x, y) in enumerate(fixed_points):
        current_ac["fixed" + str(i)] = Plane("fixed" + str(i),
                                            {"Lat": x, "Long": y,
                                             "kLat": x, "kLong": y, # for k_filter
                                             "Alt": 0, "Type": "static"})

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
        grid = make_grid(current_ac, lat_min, lat_max, long_min, long_max)
        plot(grid)
        log(current_ac)
        time.sleep(2)


def get_config_data():
    # load config file - should be config.json in project root
    try:
        with open("config.json", "r") as f:
            map_data = json.load(f)

            # check data format - should be float
            assert type(map_data["bottom_left"][0]) == float
            assert type(map_data["bottom_left"][1]) == float
            assert type(map_data["top_right"][0]) == float
            assert type(map_data["top_right"][1]) == float
            r = float(map_data["range"])
            fixed = list(filter(lambda x: type(x[0]) == float and type(x[1]) == float, map_data["fixed_points"]))
            fixed = [tuple(coord) for coord in fixed]
    except FileNotFoundError:
        print("Please configure location and map data in a config.json.")
        sys.exit(1)

    x_low, y_low = map_data["bottom_left"]
    x_high, y_high = map_data["top_right"]

    # check data is valid
    if not (x_low < x_high and y_low < y_high):
        print("invalid coordinates.")
        sys.exit(1)
    return fixed, x_low, x_high, y_low, y_high, r


if __name__ == '__main__':
    fixed, x_low, x_high, y_low, y_high, r = get_config_data()
    track(fixed, x_low, x_high, y_low, y_high, r)
