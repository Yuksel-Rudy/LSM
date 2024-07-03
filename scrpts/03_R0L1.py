import numpy as np
import matplotlib.pyplot as plt
import moorpy as mp
from shapely.geometry import Polygon
from model.lsm import LinearModel
from famodel.project import Project
import time

# # Linear Model
delta_theta = 5  # [degree]
Thrust = 1.95e6   # [N]
angles = np.radians([0, 90, 135, 180, 270, 315])
shared_status = [1, 1, 0, 1, 1, 0]
k_l = 23677.68558513264
k_t = 1208.0503802290496
ks_l = 7.20334869e+03
ks_t = 1.40852158e+03
lsm = LinearModel(inline_stiffness=k_l, 
                  transverse_stiffness=k_t,
                  shared_inline_stiffness=ks_l,
                  shared_transverse_stiffness=ks_t,
                  mooring_heading=angles,
                  shared_status=shared_status)
K_total = sum(lsm.K_lines)

# FAModel
Array = Project(file='inputs/fam_inputs/R0L1_fam.yaml',raft=0)
Array.getMoorPyArray(pristineLines=1,plt=1)


# for platform in Array.platformList:
start_time = time.time()
x, y, maxVals = Array.platformList['fowt1'].getWatchCircle(ang_spacing=delta_theta)
end_time = time.time()
et_fam = end_time - start_time
# # Create watch circles and compare
thetas = np.radians(np.arange(0, 360, delta_theta))
start_time = time.time()
wcx_l_00 = []
wcy_l_00 = []
for i, thrust_angle in enumerate(thetas):
    f = np.array([[Thrust * np.cos(thrust_angle)],[Thrust * np.sin(thrust_angle)]])
    zeta = np.linalg.inv(K_total) @ f
    wcx_l_00.append(zeta[0])
    wcy_l_00.append(zeta[1])

wcx_l_00.append(wcx_l_00[0])
wcy_l_00.append(wcy_l_00[0])
end_time = time.time()
et_lsm = end_time - start_time
print(f"ET(FAM) = {et_fam}")
print(f"ET(LSM) = {et_lsm}")
# Create a shapely out of the watch circle and compute watch circle area:
wcx_l_00 = np.array(wcx_l_00)
wcy_l_00 = np.array(wcy_l_00)
coordinates = list(zip(wcx_l_00, wcy_l_00))
polygon = Polygon(coordinates)
A_h = polygon.area

x = np.array(x)
y = np.array(y)
# x.append(x[0])
# y.append(x[0])
coordinates = list(zip(x, y))
polygon = Polygon(coordinates)
A_a = polygon.area

print(f'watch circle area (m^2)= [real:{A_a}, linear:{A_h}, linear-corrected:{None}')

fig, ax = plt.subplots()
plt.plot(wcx_l_00, wcy_l_00, color='red', label='linear')
plt.plot(x, y, color='blue', label='FAM')
plt.axis('equal')
plt.xlabel('x-coordinate')
plt.ylabel('y-coordinate')
plt.legend()
plt.show()