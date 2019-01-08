import numpy as np
import pygame
import time
from typing import Tuple


DIMS = (400, 400)

class Point:

    def __init__(self):
        self.x = DIMS[0] - 5.
        self.y = 5.
        self.dx = -1.
        self.dy = 1.

    def get_position(self):
        x, y = self.x + self.dx + np.random.randn() * 4, self.y + self.dy + np.random.randn() * 4
        self.x = self.x + self.dx
        self.y = self.y + self.dy
        return (x, y)


class KalmanFilter:
    # see http://scottlobdell.me/2014/08/kalman-filtering-python-reading-sensor-input/

    def __init__(self, process_variance: float,
                 estimated_measurement_variance: float):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = np.zeros(2)
        self.posteri_error_estimate = np.ones(2)

    def input_measurement(self, measurement: Tuple[float, float]):
        priori_estimate = self.posteri_estimate.copy()
        priori_error_estimate = self.posteri_error_estimate + self.process_variance
        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (np.array(measurement,
                                                                              dtype=np.float32) - priori_estimate)
        self.posteri_error_estimate = (1. - blending_factor) * priori_error_estimate

    def get_estimated_position(self) -> Tuple[float, float]:
        return self.posteri_estimate[0], self.posteri_estimate[1]


def demo():
    display = pygame.display.set_mode(DIMS)
    clock = pygame.time.Clock()
    done = False

    grid = np.ones(DIMS) * 255.
    p = Point()
    kf = KalmanFilter(1e-5, .05**2)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        x, y = p.get_position()
        if not (0 < x < DIMS[0] and 0 < y < DIMS[1]):
            time.sleep(10)
            break
        grid[int(x), int(y)] = 0.

        kf.input_measurement((x, y))
        kx, ky = kf.get_estimated_position()
        grid[int(kx), int(ky)] = 100.

        surf = pygame.surfarray.make_surface(grid.T)
        display.blit(surf, (0, 0))
        pygame.display.update()

        clock.tick(60)

if __name__ == '__main__':
    demo()
