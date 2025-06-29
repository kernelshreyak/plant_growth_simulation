"""
Main simulation and visualization module for the plant growth model.

This module defines the Plant class which simulates the growth of roots and shoots
based on environmental scalar fields (sunlight, temperature, moisture), including
branching and flowering dynamics. The growth process is accelerated using Numba JIT
compilation for numerical computations.

The simulation environment and parameters are configured in `plantsim_config.py`.

Visualization leverages PyQtGraph for interactive 2D view of the plant structure
including branches, roots, leaves, and flowers.

Usage:
    Run this script to perform a full simulation and display the evolving plant
    structure interactively.

Author: Shreyak Chakraborty
Date: June 29th 2025
"""

import numpy as np
from numba import njit, prange
import time
import logging
import random

# Use PyQtGraph for accelerated interactive 2D visualization
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from plantsim_config import (
    WIDTH, HEIGHT, SOIL_DEPTH, CYCLES,
    BASE_BRANCH_LEN, BRANCH_ANGLE_RANGE, BRANCH_PROB, LEAF_BASE_SIZE,
    BASE_ROOT_LEN, ROOT_ANGLE_RANGE,
    FLOWER_CYCLE_START, FLOWER_BASE_SIZE, FLOWER_COLORS
)

# ----------------------------
# Logging Configuration
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ----------------------------
# Numba-optimized scalar fields
# ----------------------------
# ----------------------------
@njit(parallel=True)
def sunlight_field(y_arr):
    n = y_arr.shape[0]; out = np.empty(n)
    for i in prange(n): out[i] = 0.5 + 0.5*np.sin(np.pi*y_arr[i]/HEIGHT)
    return out

@njit(parallel=True)
def temperature_field(x_arr):
    n = x_arr.shape[0]; out = np.empty(n)
    for i in prange(n): out[i] = 20 + 10*np.cos(np.pi*x_arr[i]/WIDTH)
    return out

@njit(parallel=True)
def moisture_field(x_arr, y_arr):
    n = x_arr.shape[0]; out = np.empty(n)
    cx, cy, sigma = WIDTH/2.0, HEIGHT/2.0, WIDTH/4.0
    for i in prange(n):
        dx, dy = x_arr[i]-cx, y_arr[i]-cy
        out[i] = 0.5 + 0.5*np.exp(-(dx*dx+dy*dy)/(2*sigma*sigma))
    return out

@njit(parallel=True)
def branch_growth(x_arr, y_arr, angle_arr, rand_off, rand_br):
    n = x_arr.shape[0]
    new_x = np.empty(n); new_y = np.empty(n)
    new_ang = np.empty(n); gf_arr = np.empty(n)
    sun = sunlight_field(y_arr)
    temp = temperature_field(x_arr)
    water = moisture_field(x_arr, y_arr)
    for i in prange(n):
        gf = sun[i]*water[i]*(1-abs(temp[i]-25)/50)
        gf_arr[i] = gf
        length = BASE_BRANCH_LEN*gf
        theta = angle_arr[i] + (rand_off[i]*2-1)*BRANCH_ANGLE_RANGE
        new_x[i] = x_arr[i] + length*np.cos(theta)
        new_y[i] = y_arr[i] + length*np.sin(theta)
        new_ang[i] = theta
    return new_x, new_y, new_ang, gf_arr

class Plant:
    def __init__(self, x0, y0):
        # initialize tips
        self.branch_tips = [{'pos': np.array([x0, y0]), 'angle': np.pi/2}]
        self.branches, self.leaves = [], []
        self.root_tips, self.roots = [{'pos': np.array([x0, y0]), 'angle': -np.pi/2}], []
        self.flowers = []  # store flower dicts: pos, size, color

    def grow(self, cycles=CYCLES):
        logger.info(f"Starting growth for {cycles} cycles...")
        for cycle in range(1, cycles+1):
            start = time.time()
            b0, r0, l0, t0, f0 = len(self.branches), len(self.roots), len(self.leaves), len(self.branch_tips), len(self.flowers)
            # above-ground
            n = len(self.branch_tips)
            if n:
                pos = np.array([tip['pos'] for tip in self.branch_tips])
                x, y = pos[:,0], pos[:,1]
                ang = np.array([tip['angle'] for tip in self.branch_tips])
                ro, rb = np.random.rand(n), np.random.rand(n)
                nx, ny, nang, gf = branch_growth(x, y, ang, ro, rb)
                new_tips = []
                for i in range(n):
                    # starting point of this segment
                    s = pos[i]
                    # compute raw end point, then clamp to ground level (y>=0)
                    raw_e = np.array([nx[i], ny[i]])
                    e = raw_e.copy()
                    if e[1] < 0:
                        e[1] = 0
                    # record branch and leaf
                    self.branches.append((s, e))
                    self.leaves.append({'pos': e, 'size': LEAF_BASE_SIZE * gf[i]})
                    new_tips.append({'pos': e, 'angle': nang[i]})
                    # possible bifurcation
                    if rb[i] < BRANCH_PROB * gf[i]:
                        th2 = ang[i] + (random.random() * 2 - 1) * BRANCH_ANGLE_RANGE
                        raw_e2 = s + BASE_BRANCH_LEN * gf[i] * np.array([np.cos(th2), np.sin(th2)])
                        e2 = raw_e2.copy()
                        if e2[1] < 0:
                            e2[1] = 0
                        self.branches.append((s, e2))
                        self.leaves.append({'pos': e2, 'size': LEAF_BASE_SIZE * gf[i]})
                        new_tips.append({'pos': e2, 'angle': th2})
                # bloom flowers after threshold cycle
                if cycle >= FLOWER_CYCLE_START:
                    for tip in new_tips:
                        color = random.choice(FLOWER_COLORS)
                        self.flowers.append({'pos': tip['pos'], 'size': FLOWER_BASE_SIZE, 'color': color})
                self.branch_tips = new_tips or self.branch_tips
            # below-ground
            new_rt = []
            for rt in self.root_tips:
                x0, y0 = rt['pos']
                w = moisture_field(np.array([x0]), np.array([y0]))[0]
                length = BASE_ROOT_LEN*w
                th = rt['angle'] + random.uniform(-ROOT_ANGLE_RANGE, ROOT_ANGLE_RANGE)
                e = rt['pos'] + length*np.array([np.cos(th), np.sin(th)])
                self.roots.append((rt['pos'], e))
                new_rt.append({'pos': e, 'angle': th})
            self.root_tips = new_rt or self.root_tips
            # logging
            b1, r1, l1, t1, f1 = len(self.branches), len(self.roots), len(self.leaves), len(self.branch_tips), len(self.flowers)
            elapsed = time.time()-start
            logger.info(
                f"Cycle {cycle:>3}: Δtips={t0}->{t1} Δbr={b1-b0} Δrt={r1-r0} Δlv={l1-l0} Δfl={f1-f0} time={elapsed:.3f}s"
            )

    def plot(self):
        """Interactive visualization with flowers"""
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        win = pg.GraphicsLayoutWidget(title="Plant Growth Simulation")
        vb = win.addViewBox(); vb.setAspectLocked(True)
        xm, xr = WIDTH/2, WIDTH*0.3
        vb.setRange(xRange=(xm-xr, xm+xr), yRange=(-SOIL_DEPTH, HEIGHT*0.6))
        # soil
        soil = QtWidgets.QGraphicsRectItem(0, -SOIL_DEPTH, WIDTH, SOIL_DEPTH)
        soil.setBrush(pg.mkBrush('sandybrown')); soil.setPen(pg.mkPen(None))
        vb.addItem(soil)
        # branches
        bx, by = [], []
        for s, e in self.branches:
            bx += [s[0], e[0], np.nan]; by += [s[1], e[1], np.nan]
        vb.addItem(pg.PlotDataItem(bx, by, pen=pg.mkPen('g', width=1)))
        # roots
        rx, ry = [], []
        for s, e in self.roots:
            rx += [s[0], e[0], np.nan]; ry += [s[1], e[1], np.nan]
        vb.addItem(pg.PlotDataItem(rx, ry, pen=pg.mkPen('brown', width=1, dash=[4,4])))
        # leaves
        xs = [lf['pos'][0] for lf in self.leaves]
        ys = [lf['pos'][1] for lf in self.leaves]
        sizes = [max(2, lf['size']*5) for lf in self.leaves]
        vb.addItem(pg.ScatterPlotItem(xs, ys, size=sizes, brush=pg.mkBrush('lightgreen'), pen=None))
        # flowers
        fx = [fl['pos'][0] for fl in self.flowers]
        fy = [fl['pos'][1] for fl in self.flowers]
        fs = [fl['size'] for fl in self.flowers]
        fc = [fl['color'] for fl in self.flowers]
        vb.addItem(pg.ScatterPlotItem(fx, fy, size=fs, brush=[pg.mkBrush(c) for c in fc], pen=None))
        win.show(); app.exec()

if __name__ == '__main__':
    # warmup
    x_dummy = np.array([WIDTH/2.0]); y_dummy = np.array([0.0])
    ang_dummy = np.array([np.pi/2]); ro, rb = np.random.rand(1), np.random.rand(1)
    branch_growth(x_dummy, y_dummy, ang_dummy, ro, rb)
    # simulate
    plant = Plant(WIDTH/2, 0)
    plant.grow(CYCLES)
    plant.plot()
