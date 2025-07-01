# Plant Growth Simulation - Release Notes v1.1

## Major Changes

- **Full Modularization**
  - Core logic split into separate modules: `main.py` (entrypoint), `plant_sim.py` (simulation), `scalar_fields.py` (Numba-accelerated fields), `gui.py` (parameter GUI), and `plantsim_config.py` (configuration).
- **PyQt6 Migration**
  - All GUI and plotting code now uses PyQt6 for improved compatibility and future-proofing.
- **Parameter Control GUI**
  - All simulation parameters are now editable via a Qt GUI before running the simulation.
  - Parameters are loaded from a single config dictionary (`DEFAULT_PARAMS`).
- **Improved Plotting**
  - PyQtGraph visualization opens in a 1920x1080 window.
  - Plot window is reliably displayed and not garbage collected.
- **Bug Fixes & Usability**
  - Fixed event loop issues with PyQt.
  - Logging is now immediate and visible during simulation.
  - All parameter usage is consistent and modular.
- **Release Notes**
  - This file documents the major changes and improvements for this release.

---

**Author:** Shreyak Chakraborty  
**Date:** July 1, 2025