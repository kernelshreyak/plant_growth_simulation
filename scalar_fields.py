"""
Scalar field definitions for the plant growth simulation.

This module provides Numba-accelerated functions for simulating environmental
scalar fields: sunlight, temperature, and soil moisture. These fields are used
by the main simulation to determine plant growth dynamics.

Author: Shreyak Chakraborty
"""

import numpy as np
from numba import njit, prange

@njit(parallel=True)
def sunlight_field(y_arr, HEIGHT):
    """
    Simulate sunlight intensity as a function of vertical position (y).
    Returns values in [0, 1], peaking at the top of the environment.
    """
    n = y_arr.shape[0]
    out = np.empty(n)
    for i in prange(n):
        out[i] = 0.5 + 0.5 * np.sin(np.pi * y_arr[i] / HEIGHT)
    return out

@njit(parallel=True)
def temperature_field(x_arr, WIDTH):
    """
    Simulate temperature as a function of horizontal position (x).
    Returns values in [10, 30], with a cosine profile across the width.
    """
    n = x_arr.shape[0]
    out = np.empty(n)
    for i in prange(n):
        out[i] = 20 + 10 * np.cos(np.pi * x_arr[i] / WIDTH)
    return out

@njit(parallel=True)
def moisture_field(x_arr, y_arr, WIDTH, HEIGHT):
    """
    Simulate soil moisture as a 2D Gaussian centered in the environment.
    Returns values in [0, 1], highest at the center.
    """
    n = x_arr.shape[0]
    out = np.empty(n)
    cx, cy, sigma = WIDTH / 2.0, HEIGHT / 2.0, WIDTH / 4.0
    for i in prange(n):
        dx, dy = x_arr[i] - cx, y_arr[i] - cy
        out[i] = 0.5 + 0.5 * np.exp(-(dx * dx + dy * dy) / (2 * sigma * sigma))
    return out