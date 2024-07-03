import numpy as np
import matplotlib.pyplot as plt
import moorpy as mp
from shapely.geometry import Polygon
from model.lsm import LinearModel


depth = 600
angles = np.radians([0, 90, 135, 180, 270, 315])
rAnchor = 1600
zFair = 0
rFair = 0
lineLength = 1808
typeName = "chain"

ms = mp.System(depth=depth)
ms.setLineType(dnommm=120, material='chain', name=typeName)
ms.addBody(0, [0, 0, 0, 0, 0, 0], m=1e6, v=1e3, rM=100, AWP=1e3)
for i, angle in enumerate(angles):
    ms.addPoint(1, [rAnchor*np.cos(angle), rAnchor*np.sin(angle), -depth])
    ms.addPoint(1, [  rFair*np.cos(angle),   rFair*np.sin(angle),  zFair])
    ms.bodyList[0].attachPoint(2*i+2, [rFair*np.cos(angle), rFair*np.sin(angle), zFair]) 
    ms.addLine(lineLength, typeName, pointA=2*i+1, pointB=2*i+2)

ms.initialize()
ms.solveEquilibrium()
fig, ax = ms.plot()
print(f"Body offset position is {ms.bodyList[0].r6}")

# Compute nonlinear matrices:
Kn_lines = []
for line in ms.lineList:
    Kn_line = line.KB[0:2, 0:2]
    Kn_lines.append(Kn_line)

# Linear Model
k_l = 23677.68558513264
k_t = 1208.0503802290496
lsm = LinearModel(inline_stiffness=k_l,
                 transverse_stiffness=k_t,
                 shared_inline_stiffness=k_l,
                 shared_transverse_stiffness=k_t,
                 mooring_heading=angles,
                 shared_status=np.zeros_like(angles))

K_total = sum(lsm.K_lines)
# Corrected linear model
lsm.compute_C_line(Kn_lines)
corrected_K_lines = lsm.correct_K_line()
print(lsm.C_lines)
K_total_corrected = sum(corrected_K_lines)
# Create watch circles and compare

Thrust = 2.7e6   # [N]
delta_theta = 5  # [degree]
thetas = np.radians(np.arange(0, 360, delta_theta))
wcx_00 = []
wcy_00 = []
wcx_l_00 = []
wcy_l_00 = []
wcx_lc_00 = []
wcy_lc_00 = []
for i, thrust_angle in enumerate(thetas):
    ms.bodyList[0].f6Ext = np.array([Thrust * np.cos(thrust_angle), Thrust * np.sin(thrust_angle), 0, 0, 0, 0])
    ms.solveEquilibrium3(DOFtype='both')  
    wcx_00.append(ms.bodyList[0].r6[0])
    wcy_00.append(ms.bodyList[0].r6[1])
    f = np.array([[Thrust * np.cos(thrust_angle)],[Thrust * np.sin(thrust_angle)]])
    zeta = np.linalg.inv(K_total) @ f
    wcx_l_00.append(zeta[0])
    wcy_l_00.append(zeta[1])
    zetac = np.linalg.inv(K_total_corrected) @ f
    wcx_lc_00.append(zetac[0])
    wcy_lc_00.append(zetac[1])

wcx_00.append(wcx_00[0])
wcy_00.append(wcy_00[0])
wcx_l_00.append(wcx_l_00[0])
wcy_l_00.append(wcy_l_00[0])
wcx_lc_00.append(wcx_lc_00[0])
wcy_lc_00.append(wcy_lc_00[0])


# Create a shapely out of the watch circle and compute watch circle area:
wcx_00 = np.array(wcx_00)
wcy_00 = np.array(wcy_00)
coordinates = list(zip(wcx_00, wcy_00))
polygon = Polygon(coordinates)
A_a = polygon.area

wcx_l_00 = np.array(wcx_l_00)
wcy_l_00 = np.array(wcy_l_00)
coordinates = list(zip(wcx_l_00, wcy_l_00))
polygon = Polygon(coordinates)
A_h = polygon.area

wcx_lc_00 = np.array(wcx_lc_00)
wcy_lc_00 = np.array(wcy_lc_00)
coordinates = list(zip(wcx_lc_00, wcy_lc_00))
polygon = Polygon(coordinates)
A_hc = polygon.area

print(f'watch circle area (m^2)= [real:{A_a}, linear:{A_h}, linear-corrected:{A_hc}')

fig, ax = plt.subplots()
plt.plot(wcx_00, wcy_00, color='blue', label='MoorPy')
plt.plot(wcx_l_00, wcy_l_00, color='red', label='linear')
plt.plot(wcx_lc_00, wcy_lc_00, color='green', label='linear-corrected')
plt.axis('equal')
plt.xlabel('x-coordinate')
plt.ylabel('y-coordinate')
plt.legend()
plt.show()