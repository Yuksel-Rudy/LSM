import numpy as np
import matplotlib.pyplot as plt
from model.lsm import LinearModel

# Check input files R1Nx. Replace x with the xx or yy periodicity number required.
Thrust = 1.95e6   # [N]
delta_theta = 5  # [degree]

# # Linear Model
LSM_FILE = "inputs/lsm_input/R1Nxx1.yaml"
lsm = LinearModel(input_file=LSM_FILE)

# linear
x, y = lsm.get_array_watch_circle(force=Thrust,
                                  delta_theta=delta_theta,
                                  corrected=False,
                                  magnify_watch_circle=5)


fig, ax = lsm.plot(labels=True)


plt.legend()
plt.show()