import numpy as np
import matplotlib.pyplot as plt
import moorpy as mp
from model.lsm import LinearModel


depth = 600
angles1 = np.radians([0, 120, 240])
angles2 = np.radians([60, 180, 300])
rAnchor = 1600
zFair = 0
rFair = 0
lineLength = 1808
lineLength_shared = 1700
typeName = "chain"

ms = mp.System(depth=depth)
ms.setLineType(dnommm=120, material='chain', name=typeName)
ms.addBody(0, [0, 0, 0, 0, 0, 0], m=1e6, v=1e3, rM=100, AWP=1e3)
ms.addBody(0, [1600, 0, 0, 0, 0, 0], m=1e6, v=1e3, rM=100, AWP=1e3)
for i, angle in enumerate(angles1):
    ms.addPoint(1, [rAnchor*np.cos(angle) + 1600, rAnchor*np.sin(angle), -depth])
    ms.addPoint(1, [  rFair*np.cos(angle) + 1600,   rFair*np.sin(angle),  zFair])
    ms.bodyList[0].attachPoint(2*i+2, [rFair*np.cos(angle), rFair*np.sin(angle), zFair]) 
    ms.addLine(lineLength, typeName, pointA=2*i+1, pointB=2*i+2)
pointlistlength = len(ms.pointList)
for i, angle in enumerate(angles2):
    ms.addPoint(1, [rAnchor*np.cos(angle), rAnchor*np.sin(angle), -depth])
    ms.addPoint(1, [  rFair*np.cos(angle),   rFair*np.sin(angle),  zFair])
    ms.bodyList[1].attachPoint(pointlistlength + 2*i+2, [rFair*np.cos(angle), rFair*np.sin(angle), zFair]) 
    ms.addLine(lineLength, typeName, pointA=pointlistlength + 2*i+1, pointB=pointlistlength + 2*i+2)

ms.addLine(lineLength_shared, typeName, pointA=2, pointB=pointlistlength+2)
# ms.bodyList[0].f6Ext = np.array([-2.5e6, 0, 0, 0, 0, 0])
ms.initialize()
ms.solveEquilibrium()
fig, ax = ms.plot()
plt.show()
print(f"K = {ms.lineList[6].KA}")