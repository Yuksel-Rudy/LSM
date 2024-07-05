import numpy as np
import matplotlib.pyplot as plt
from model.lsm import LinearModel

Thrust = 1.95e6   # [N]
delta_theta = 5  # [degree]

# # Linear Model
LSM_FILE = "inputs/lsm_input/test2.yaml"
lsm = LinearModel(input_file=LSM_FILE)

# linear
x, y = lsm.get_array_watch_circle(force=Thrust,
                                  delta_theta=delta_theta,
                                  corrected=False)


fig, ax = plt.subplots()

for i, block in enumerate(lsm.array):
    for j in np.arange(len(lsm.blocks[block['name']].fowts)):
        plt.plot(x[i][j], y[i][j], color='red', label='linear' if i==0 and j==0 else None)
        # plt.plot(x_a, y_a, color='blue', label='FAM')
        plt.axis('equal')
        plt.xlabel('x-coordinate')
        plt.ylabel('y-coordinate')

# plt.legend()
plt.show()