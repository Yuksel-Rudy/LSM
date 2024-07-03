import numpy as np
import matplotlib.pyplot as plt
import moorpy as mp
from model.lsm import LinearModel


depth = 600
angles = np.radians([0, 120, 240])
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

# ms.bodyList[0].f6Ext = np.array([-2.5e6, 0, 0, 0, 0, 0])
ms.initialize()
ms.solveEquilibrium()
fig, ax = ms.plot()
print(f"Body offset position is {ms.bodyList[0].r6}")
unloaded_surge = ms.bodyList[0].r6[0]
unloaded_tension_0 = ms.lineList[0].HF
unloaded_tension_1 = ms.lineList[1].HF
unloaded_tension_2 = ms.lineList[2].HF
deltaThrust = 0.1e5   # [N]
deltaThrust_angle = 180
ms.bodyList[0].f6Ext = np.array([deltaThrust * np.cos(deltaThrust_angle), deltaThrust * np.sin(deltaThrust_angle), 0, 0, 0, 0])
ms.solveEquilibrium3(DOFtype='both')  
print(f"Body offset position is {ms.bodyList[0].r6}")
ms.plot(ax=ax, color='red')
loaded_surge = ms.bodyList[0].r6[0]
loaded_tension_0 = ms.lineList[0].HF
loaded_tension_1 = ms.lineList[1].HF
loaded_tension_2 = ms.lineList[2].HF

delta_t = loaded_tension_0 - unloaded_tension_0
delta_l = np.abs(loaded_surge - unloaded_surge)


k_l = delta_t/delta_l  # [N/m]
k_t = unloaded_tension_1/lineLength

# Compute nonlinear matrices:
Kn_lines = []
for line in ms.lineList:
    Kn_line = line.KB[0:2, 0:2]
    Kn_lines.append(Kn_line)

lm = LinearModel(inline_stiffness=k_l,
                 transverse_stiffness=k_t,
                 shared_inline_stiffness=k_l,
                 shared_transverse_stiffness=k_t,
                 mooring_heading=angles,
                 shared_status=np.zeros_like(angles))
lm.compute_C_line(Kn_lines)
corrected_K_lines = lm.correct_K_line()
K_total = sum(lm.K_lines)
K_total_corrected = sum(corrected_K_lines)

deltaThrust = 2.7e6   # [N]
delta_theta = 5  # [degree]
thetas = np.radians(np.arange(0, 360, delta_theta))
wcx_00 = []
wcy_00 = []
wcx_l_00 = []
wcy_l_00 = []
wcx_lc_00 = []
wcy_lc_00 = []
for i, deltaThrust_angle in enumerate(thetas):
    ms.bodyList[0].f6Ext = np.array([deltaThrust * np.cos(deltaThrust_angle), deltaThrust * np.sin(deltaThrust_angle), 0, 0, 0, 0])
    ms.solveEquilibrium3(DOFtype='both')  
    wcx_00.append(ms.bodyList[0].r6[0])
    wcy_00.append(ms.bodyList[0].r6[1])
    f = np.array([[deltaThrust * np.cos(deltaThrust_angle)],[deltaThrust * np.sin(deltaThrust_angle)]])
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
fig, ax = plt.subplots()
plt.plot(wcx_00, wcy_00, color='blue', label='MoorPy')
plt.plot(wcx_l_00, wcy_l_00, color='red', label='linear')
plt.plot(wcx_lc_00, wcy_lc_00, color='green', label='linear-corrected')
plt.axis('equal')
plt.xlabel('x-coordinate')
plt.ylabel('y-coordinate')
plt.legend()
plt.show()

print(f"k_l = {k_l}")
print(f"k_t = {k_t}")