from PyQt6 import QtWidgets
from copy import deepcopy
from plant_sim import Plant

class ParamGui(QtWidgets.QWidget):
    """
    Qt GUI for editing simulation parameters and running the simulation.
    """
    def __init__(self, default_params):
        super().__init__()
        self.setWindowTitle("Plant Growth Simulation - Parameter Control")
        self.params = deepcopy(default_params)
        self.inputs = {}
        self.plot_window = None  # Hold reference to plot window
        layout = QtWidgets.QFormLayout()
        # Add input fields for all numeric parameters
        for key, val in self.params.items():
            if isinstance(val, (int, float)):
                inp = QtWidgets.QLineEdit(str(val))
                self.inputs[key] = inp
                layout.addRow(key, inp)
            elif isinstance(val, list):
                inp = QtWidgets.QLineEdit(','.join(map(str, val)))
                self.inputs[key] = inp
                layout.addRow(key, inp)
        self.run_btn = QtWidgets.QPushButton("Run Simulation")
        self.run_btn.clicked.connect(self.run_simulation)
        layout.addRow(self.run_btn)
        self.setLayout(layout)

    def run_simulation(self):
        # Read values from inputs
        for key, inp in self.inputs.items():
            val = inp.text()
            if key == "FLOWER_COLORS":
                self.params[key] = [s.strip() for s in val.split(',') if s.strip()]
            else:
                try:
                    if '.' in val or 'e' in val.lower():
                        self.params[key] = float(val)
                    else:
                        self.params[key] = int(val)
                except Exception:
                    self.params[key] = float(val) if '.' in val else val
        # Run simulation with current parameters
        width = self.params["WIDTH"]
        plant = Plant(width/2, 0, self.params)
        plant.grow(self.params["CYCLES"])
        self.plot_plant(plant)

    def plot_plant(self, plant):
        # Inline import to avoid circular import
        import pyqtgraph as pg
        from PyQt6 import QtWidgets as PGQtWidgets
        params = plant.params
        # Hold reference to window to prevent garbage collection
        self.plot_window = pg.GraphicsLayoutWidget(title="Plant Growth Simulation")
        self.plot_window.resize(1366,768)
        vb = self.plot_window.addViewBox()
        vb.setAspectLocked(True)
        xm, xr = params["WIDTH"] / 2, params["WIDTH"] * 0.3
        vb.setRange(xRange=(xm - xr, xm + xr), yRange=(-params["SOIL_DEPTH"], params["HEIGHT"] * 0.6))
        # Draw soil as a rectangle
        soil = PGQtWidgets.QGraphicsRectItem(0, -params["SOIL_DEPTH"], params["WIDTH"], params["SOIL_DEPTH"])
        soil.setBrush(pg.mkBrush('sandybrown'))
        soil.setPen(pg.mkPen(None))
        vb.addItem(soil)
        # Draw branches as green lines
        bx, by = [], []
        for s, e in plant.branches:
            bx += [s[0], e[0], float('nan')]
            by += [s[1], e[1], float('nan')]
        vb.addItem(pg.PlotDataItem(bx, by, pen=pg.mkPen('g', width=1)))
        # Draw roots as dashed brown lines
        rx, ry = [], []
        for s, e in plant.roots:
            rx += [s[0], e[0], float('nan')]
            ry += [s[1], e[1], float('nan')]
        vb.addItem(pg.PlotDataItem(rx, ry, pen=pg.mkPen('brown', width=1, dash=[4, 4])))
        # Draw leaves as light green circles
        xs = [lf['pos'][0] for lf in plant.leaves]
        ys = [lf['pos'][1] for lf in plant.leaves]
        sizes = [max(2, lf['size'] * 5) for lf in plant.leaves]
        vb.addItem(pg.ScatterPlotItem(xs, ys, size=sizes, brush=pg.mkBrush('lightgreen'), pen=None))
        # Draw flowers as colored circles
        fx = [fl['pos'][0] for fl in plant.flowers]
        fy = [fl['pos'][1] for fl in plant.flowers]
        fs = [fl['size'] for fl in plant.flowers]
        fc = [fl['color'] for fl in plant.flowers]
        vb.addItem(pg.ScatterPlotItem(fx, fy, size=fs, brush=[pg.mkBrush(c) for c in fc], pen=None))
        self.plot_window.show()
        QtWidgets.QApplication.processEvents()
