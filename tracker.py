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
    data = [" ".join((str(p.Lat), str(p.Long), str(p.colour))) for p in planes.values()]
    with open("log.txt", "a") as f:
        f.write(t + " - " + " - ".join(data) + "\n")


def make_grid(planes: Dict[str, Plane], grid: np.ndarray) -> np.ndarray:
    x_low, x_high = 53.28, 53.54
    y_low, y_high = -2.45, -2.06
    grid[:, :, 2] /= 1.8
    grid[grid[:, :, 2] < .1] = 0.
    for plane in planes.values():
        lat, long = plane.Lat, plane.Long
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


def tracker(lat: float, long: float, r: float = 25.) -> None:
    url = "http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat={}&lng={}&fDstL=0&fDstU={}".format(
        lat, long, r)
    current_ac = {}
    # add fixed point(s)
    home = Plane("home", {"Lat": lat, "Long": long,
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
        grid = make_grid(current_ac, grid)
        plot(grid)
        log(current_ac)
        time.sleep(4)


if __name__ == '__main__':
    coords = (51.47, -0.45)
    tracker(coords[0], coords[1], 22.)
