"""
Main entrypoint for the plant growth simulation.

Launches the Qt GUI for parameter control and simulation.
"""

import logging
from PyQt6 import QtWidgets
from gui import ParamGui
from plantsim_config import DEFAULT_PARAMS

# Ensure logging is configured for immediate output
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
    force=True
)

if __name__ == '__main__':
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    gui = ParamGui(DEFAULT_PARAMS)
    gui.show()
    app.exec()
