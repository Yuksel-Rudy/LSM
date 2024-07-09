import numpy as np
import matplotlib.pyplot as plt
from model.lsm import LinearModel

# Check input files R0Lx. Replace x with the level number required.
Thrust = 2.478302e6   # [N]
delta_theta = 5  # [degree]

# # Linear Model
LSM_FILE = "inputs/lsm_input/TRTLE(S).yaml"
lsm = LinearModel(input_file=LSM_FILE)

# linear
x, y = lsm.get_array_watch_circle(force=Thrust,
                                  delta_theta=delta_theta,
                                  corrected=False,
                                  magnify_watch_circle=1)

r = np.sqrt(np.array(x[0][0], dtype=float)**2 + np.array(y[0][0], dtype=float)**2)
rmax = r.max()
fig, ax = lsm.plot(labels=True)


plt.legend()
plt.show()