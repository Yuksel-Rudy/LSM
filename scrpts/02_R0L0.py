from model.lsm import LinearModel
import moorpy as mp
import matplotlib.pyplot as plt
import numpy as np

# Nonlinear Model
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
ms.plot()
plt.show()
Kn_lines = []
for line in ms.lineList:
    Kn_line = line.KB[0:2, 0:2]
    Kn_lines.append(Kn_line)

LSM_FILE = "inputs/lsm_input/R0L0.yaml"
lsm = LinearModel(input_file=LSM_FILE)

# Corrected linear model
lsm.unit_cells['center'].lin2nonlin_corr(Kn_lines=Kn_lines)

# Create watch circles and compare
Thrust = 2.7e6   # [N]
delta_theta = 5  # [degree]
# linear
x, y = lsm.get_array_watch_circle(force=Thrust,
                                  delta_theta=delta_theta,
                                  corrected=False)

# linear-corrected
x_c, y_c = lsm.get_array_watch_circle(force=Thrust,
                                  delta_theta=delta_theta,
                                  corrected=True)
# nonlinear
x_a, y_a = [], []
for thrust_angle in np.radians(np.arange(0, 360, delta_theta)):
    ms.bodyList[0].f6Ext = np.array([Thrust * np.cos(thrust_angle), Thrust * np.sin(thrust_angle), 0, 0, 0, 0])
    ms.solveEquilibrium3(DOFtype='both')  
    x_a.append(ms.bodyList[0].r6[0])
    y_a.append(ms.bodyList[0].r6[1])
x_a.append(x_a[0])
y_a.append(y_a[0])

fig, ax = plt.subplots()
plt.plot(x_a, y_a, label='watch circle: nonlinear', color='red')
for i, block in enumerate(lsm.array):
    for j in np.arange(len(lsm.blocks[block['name']].fowts)):
        plt.plot(x[i][j], y[i][j], label='watch circle: linear', color='blue')
        plt.plot(x_c[i][j], y_c[i][j], label='watch circle: linear-corrected', color='green')

plt.axis('equal')
plt.xlabel('x-coordinate')
plt.ylabel('y-coordinate')
plt.legend()
plt.show()