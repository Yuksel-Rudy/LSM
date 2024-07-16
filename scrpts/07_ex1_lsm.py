import matplotlib.pyplot as plt
from model.lsm2 import LinearModel


Thrust = 1.95e6   # [N]
delta_theta = 5  # [degree]
input_file_BL = "inputs/lsm_input/ex1_BL.yaml"
input_file_UC = "inputs/lsm_input/ex1_UC.yaml"

BL = LinearModel(input_file_BL)
UC = LinearModel(input_file_UC)

fig, ax = plt.subplots()
BL.plot_wc(ax=ax, force=Thrust, delta_theta=delta_theta, color="blue", label="BL")
# UC.plot_wc(ax=ax, force=Thrust, delta_theta=delta_theta, color="red", label="UC", anchor_and_mooring=False)
plt.legend()
plt.show()