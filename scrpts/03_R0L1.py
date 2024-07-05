import numpy as np
import matplotlib.pyplot as plt
import moorpy as mp
from shapely.geometry import Polygon
from model.lsm import LinearModel
from famodel.project import Project
import time

Thrust = 1.95e6   # [N]
delta_theta = 5  # [degree]

# FAModel
Array = Project(file='inputs/fam_inputs/R0L1_fam.yaml',raft=0)
Array.getMoorPyArray(pristineLines=1,plt=1)


# for platform in Array.platformList:
start_time = time.time()
x_a, y_a, maxVals = Array.platformList['fowt1'].getWatchCircle(ang_spacing=delta_theta)
end_time = time.time()
et_fam = end_time - start_time

# # Linear Model
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

start_time = time.time()
x, y = lsm.get_watch_circle(center_x=0.0,
                            center_y=0.0,
                            force=Thrust,
                            delta_theta=delta_theta,
                            unit_cell_name="center",
                            unit_heading=90.00,  # the FAM model has a different setup 
                            corrected=False)
end_time = time.time()
et_lsm = end_time - start_time

print(f"ET(FAM) = {et_fam}")
print(f"ET(LSM) = {et_lsm}")

# Create a shapely out of the watch circle and compute watch circle area:
x = np.array(x)
y = np.array(y)
coordinates = list(zip(x, y))
polygon = Polygon(coordinates)
A_h = polygon.area

x_a = np.array(x_a)
y_a = np.array(y_a)
coordinates = list(zip(x_a, y_a))
polygon = Polygon(coordinates)
A_a = polygon.area

print(f'watch circle area (m^2)= [real:{A_a}, linear:{A_h}, linear-corrected:{None}')

fig, ax = plt.subplots()
plt.plot(x, y, color='red', label='linear')
plt.plot(x_a, y_a, color='blue', label='FAM')
plt.axis('equal')
plt.xlabel('x-coordinate')
plt.ylabel('y-coordinate')
plt.legend()
plt.show()