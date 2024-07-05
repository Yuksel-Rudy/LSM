import numpy as np
import matplotlib.pyplot as plt
import moorpy as mp
from shapely.geometry import Polygon
from model.lsm import LinearModel
from famodel.project import Project
import time


# Linear Model
LMG_FILE = "inputs/linear_group_mooring_input/lmg_01.yaml"
lsm = LinearModel(linear_group_mooring_file=LMG_FILE)

# create a unit cell - center
cell_name = "center"
angles = np.radians([0, 90, 135, 180, 270, 315])  # starting from E going +CW
lmg = ["shared line", "shared line", "anchored line", "shared line", "shared line", "anchored line"]
mooring = {}
mooring["mooring_heading"] = angles
mooring["lmg"] = lmg
lsm.create_unit_cell(name=cell_name, mooring=mooring)

# create a unit cell - boundary
cell_name = "boundary"
angles = np.radians([0, 90, 180, 270])  # starting from E going +CW
lmg = ["anchored line", "shared line", "anchored line", "anchored line"]
mooring = {}
mooring["mooring_heading"] = angles
mooring["lmg"] = lmg
lsm.create_unit_cell(name=cell_name, mooring=mooring)

block = {
    "fowt1": {"center_x": 0.0,     "center_y": 0.0,     "unit_heading": 0.0,   "cell": "center"},
    "fowt2": {"center_x": 0.0,     "center_y": 1600.0,  "unit_heading": 0.0,   "cell": "boundary"},
    "fowt3": {"center_x": 1600.0,  "center_y": 0.0,     "unit_heading": 90.0,  "cell": "boundary"},
    "fowt4": {"center_x": 0.0,     "center_y": -1600.0, "unit_heading": 180.0, "cell": "boundary"},
    "fowt5": {"center_x": -1600.0, "center_y": 0.0,     "unit_heading": 270.0, "cell": "boundary"}
}

# Compute watch circles
Thrust = 1.95e6   # [N]
delta_theta = 5  # [degree]

fig, ax = plt.subplots()
for fowt_name, fowt_data in block.items():
    x, y = lsm.get_watch_circle(force=Thrust,
                                delta_theta=delta_theta,
                                unit_cell_name=fowt_data["cell"],
                                unit_heading=fowt_data["unit_heading"],
                                center_x=fowt_data["center_x"],
                                center_y=fowt_data["center_y"])
    plt.plot(x, y, color='red')

plt.axis('equal')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Block-R0L1')
# plt.legend()
plt.grid(True)
plt.show()
