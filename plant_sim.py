import numpy as np
import random
import time
import logging
from numba import njit, prange
from scalar_fields import sunlight_field, temperature_field, moisture_field

logger = logging.getLogger(__name__)

@njit(parallel=True)
def branch_growth(x_arr, y_arr, angle_arr, rand_off, rand_br, BASE_BRANCH_LEN, BRANCH_ANGLE_RANGE, WIDTH, HEIGHT):
    """
    Compute the next positions and angles for all current branch tips.

    Parameters:
        x_arr, y_arr: Arrays of current tip positions.
        angle_arr: Array of current tip angles (radians).
        rand_off: Array of random offsets for angle perturbation.
        rand_br: Array of random values for bifurcation probability.
        BASE_BRANCH_LEN, BRANCH_ANGLE_RANGE, WIDTH, HEIGHT: Simulation parameters.

    Returns:
        new_x, new_y: Arrays of new tip positions.
        new_ang: Array of new tip angles.
        gf_arr: Array of growth factors for each tip.

    Growth factor (gf) is determined by sunlight, moisture, and temperature at each tip.
    """
    n = x_arr.shape[0]
    new_x = np.empty(n)
    new_y = np.empty(n)
    new_ang = np.empty(n)
    gf_arr = np.empty(n)
    sun = sunlight_field(y_arr, HEIGHT)
    temp = temperature_field(x_arr, WIDTH)
    water = moisture_field(x_arr, y_arr, WIDTH, HEIGHT)
    for i in prange(n):
        gf = sun[i] * water[i] * (1 - abs(temp[i] - 25) / 50)
        gf_arr[i] = gf
        length = BASE_BRANCH_LEN * gf
        theta = angle_arr[i] + (rand_off[i] * 2 - 1) * BRANCH_ANGLE_RANGE
        new_x[i] = x_arr[i] + length * np.cos(theta)
        new_y[i] = y_arr[i] + length * np.sin(theta)
        new_ang[i] = theta
    return new_x, new_y, new_ang, gf_arr

class Plant:
    """
    Simulates a plant with above-ground (branches, leaves, flowers) and below-ground (roots) structures.

    Methods:
        grow(cycles): Simulate plant growth for a given number of cycles.
        plot():      Visualize the plant interactively using PyQtGraph.
    """
    def __init__(self, x0, y0, params):
        self.params = params
        self.branch_tips = [{'pos': np.array([x0, y0]), 'angle': np.pi/2}]
        self.branches = []
        self.leaves = []
        self.root_tips = [{'pos': np.array([x0, y0]), 'angle': -np.pi/2}]
        self.roots = []
        self.flowers = []

    def grow(self, cycles=None):
        if cycles is None:
            cycles = self.params["CYCLES"]
        logger.info(f"Starting growth for {cycles} cycles...")
        for cycle in range(1, cycles+1):
            start = time.time()
            b0, r0, l0, t0, f0 = len(self.branches), len(self.roots), len(self.leaves), len(self.branch_tips), len(self.flowers)
            n = len(self.branch_tips)
            if n:
                pos = np.array([tip['pos'] for tip in self.branch_tips])
                x, y = pos[:,0], pos[:,1]
                ang = np.array([tip['angle'] for tip in self.branch_tips])
                ro, rb = np.random.rand(n), np.random.rand(n)
                nx, ny, nang, gf = branch_growth(
                    x, y, ang, ro, rb,
                    self.params["BASE_BRANCH_LEN"],
                    self.params["BRANCH_ANGLE_RANGE"],
                    self.params["WIDTH"],
                    self.params["HEIGHT"]
                )
                new_tips = []
                for i in range(n):
                    s = pos[i]
                    raw_e = np.array([nx[i], ny[i]])
                    e = raw_e.copy()
                    if e[1] < 0:
                        e[1] = 0
                    self.branches.append((s, e))
                    self.leaves.append({'pos': e, 'size': self.params["LEAF_BASE_SIZE"] * gf[i]})
                    new_tips.append({'pos': e, 'angle': nang[i]})
                    if rb[i] < self.params["BRANCH_PROB"] * gf[i]:
                        th2 = ang[i] + (random.random() * 2 - 1) * self.params["BRANCH_ANGLE_RANGE"]
                        raw_e2 = s + self.params["BASE_BRANCH_LEN"] * gf[i] * np.array([np.cos(th2), np.sin(th2)])
                        e2 = raw_e2.copy()
                        if e2[1] < 0:
                            e2[1] = 0
                        self.branches.append((s, e2))
                        self.leaves.append({'pos': e2, 'size': self.params["LEAF_BASE_SIZE"] * gf[i]})
                        new_tips.append({'pos': e2, 'angle': th2})
                if cycle >= self.params["FLOWER_CYCLE_START"]:
                    for tip in new_tips:
                        color = random.choice(self.params["FLOWER_COLORS"])
                        self.flowers.append({'pos': tip['pos'], 'size': self.params["FLOWER_BASE_SIZE"], 'color': color})
                self.branch_tips = new_tips or self.branch_tips
            new_rt = []
            for rt in self.root_tips:
                x0, y0 = rt['pos']
                w = moisture_field(
                    np.array([x0]), np.array([y0]),
                    self.params["WIDTH"], self.params["HEIGHT"]
                )[0]
                length = self.params["BASE_ROOT_LEN"] * w
                th = rt['angle'] + random.uniform(-self.params["ROOT_ANGLE_RANGE"], self.params["ROOT_ANGLE_RANGE"])
                e = rt['pos'] + length * np.array([np.cos(th), np.sin(th)])
                self.roots.append((rt['pos'], e))
                new_rt.append({'pos': e, 'angle': th})
            self.root_tips = new_rt or self.root_tips
            b1, r1, l1, t1, f1 = len(self.branches), len(self.roots), len(self.leaves), len(self.branch_tips), len(self.flowers)
            elapsed = time.time() - start
            logger.info(
                f"Cycle {cycle:>3}: Δtips={t0}->{t1} Δbr={b1-b0} Δrt={r1-r0} Δlv={l1-l0} Δfl={f1-f0} time={elapsed:.3f}s"
            )