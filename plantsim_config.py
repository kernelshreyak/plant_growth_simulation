import numpy as np

# ----------------------------
# Simulation Configuration
# ----------------------------

DEFAULT_PARAMS = {
    # Domain and time settings:
    "WIDTH": 100,                # Width of the soil patch (horizontal extent where root and shoot operate)
    "HEIGHT": 100,               # Maximum vertical extent of shoots above the soil surface
    "SOIL_DEPTH": 20,            # Depth of the soil layer below y=0 (roots grow into negative y)
    "CYCLES": 60,                # Number of discrete growth iterations (time steps) to simulate

    # Branch growth parameters (above-ground shoots):
    "BASE_BRANCH_LEN": 1.0,      # Base segment length; scaled by environmental growth factor
    "BRANCH_ANGLE_RANGE": np.pi/6,  # Max angular deviation (± radians) per cycle for branch direction
    "BRANCH_PROB": 0.35,         # Probability that an active branch tip will bifurcate each cycle
    "LEAF_BASE_SIZE": 1.5,       # Base multiplier for leaf size; actual size = LEAF_BASE_SIZE × growth factor

    # Root growth parameters (below-ground roots):
    "BASE_ROOT_LEN": 0.5,        # Base segment length; scaled by local soil moisture
    "ROOT_ANGLE_RANGE": np.pi/8, # Max angular deviation (± radians) per cycle for root direction

    # Flowering parameters (for late-cycle blooms):
    "FLOWER_CYCLE_START": 40,    # Cycle after which flowers begin to appear on new branch tips
    "FLOWER_BASE_SIZE": 5,       # Base marker size for flowers in the plot
    "FLOWER_COLORS": ['red', 'pink', 'orange'],  # Color palette for randomly assigned flower colors
}
