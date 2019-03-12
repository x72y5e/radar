from geopy.distance import distance
from math import radians, degrees, cos, sin, sqrt, atan2
from collections import namedtuple


Point = namedtuple("Point", ["x", "y"])
Bearing = namedtuple("Bearing", ["rads", "degs"])


class Navigator(object):

    def __init__(self, pos=(53.4, -2.2)):
        self.pos = Point(pos[0], pos[1])
        print("navigator initialised")
        print("current position: ({}, {})".format(self.pos.x, self.pos.y))

    def generate_waypoints(self, destination, sectors):
        """
        :param destination: destination as point object (x = long, y = lat)
        :param interval: number of waypoints as divisor of route distance e.g. 10
        :return: list of waypoints e.g. (52, -5)
        """
        fractions = [round((1 / sectors) * x, 2) for x in range(sectors)][1:]
        waypoints = [self.get_waypoint(destination, f) for f in fractions]
        return waypoints

    def get_waypoint(self, destination, fraction):
        """
        :param destination: destination as point object (x = long, y = lat)
        :param fraction: fraction of the trajectory covered
        :return: coordinate of waypoint at fraction
        """
        f = fraction
        lat1, long1 = radians(self.pos.y), radians(self.pos.x)
        lat2, long2 = radians(destination.y), radians(destination.x)
        d = distance((self.pos.y, self.pos.x), (destination.y, destination.x)).kilometers
        d /= 6371
        a = sin((1 - f) * d) / sin(d)
        b = sin(f * d) / sin(d)
        x = a * cos(lat1) * cos(long1) + b * cos(lat2) * cos(long2)
        y = a * cos(lat1) * sin(long1) + b * cos(lat2) * sin(long2)
        z = a * sin(lat1) + b * sin(lat2)
        wp_long = round(degrees(atan2(z, sqrt((x * x) + (y * y)))), 2)
        wp_lat = round(degrees(atan2(y, x)), 2)
        return ((wp_lat, wp_long))



if __name__ == '__main__':
    n = Navigator()
    warsaw = Point(52.10, 20.98)
    phil = Point(40, -75)
    d = Point(-115, 32)
    wp = n.generate_waypoints(phil, 3)
    for p in wp:
        print(p)
