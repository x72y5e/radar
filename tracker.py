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
    lat, long = fixed_points[0]
    print("getting data...")
    url = "http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat={}&lng={}&fDstL=0&fDstU={}".format(
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


if __name__ == '__main__':
    bleft = input("enter coordinate (in format lat, long) for bottom-left of the map: (or press enter for default) ")
    tright = input("enter coordinate (in format lat, long) for top-right of the map: (or press enter for default)")
    fixed = []
    while True:
        fp = input("enter coordinates (in format lat, long) for any fixed point, or press enter to continue: ")
        if fp:
            fixed.append([float(x) for x in fp.split(",")])
        else:
            break

    if bleft and tright:
        try:
            x_low, y_low = [float(x) for x in bleft.split(",")]
            x_high, y_high = [float(x) for x in tright.split(",")]
        except Exception as e:
            print("wrong format.\n", e)
            sys.exit(1)
    else:
        x_low, x_high, y_low, y_high = 51.41, 51.53, -.7, -.24

    if not fixed:
        fixed = [(51.47, -0.45)]

    # check data is valid
    if not (x_low < x_high and y_low < y_high):
        print("invalid coordinates.")
        sys.exit(1)

    track(fixed, x_low, x_high, y_low, y_high, 18.)
