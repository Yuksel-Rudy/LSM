import numpy as np
import matplotlib.pyplot as plt
from model.lsm import LinearModel
from model.line import Line
import yaml
from shapely.geometry import Polygon

def get_stiffness(lines, group_name, OP):
    for line in lines:
        if line.group_name == group_name:
            for data in line.stiffness_matrices:
                if data['OP'] == OP:
                    return data['stiffness_matrix']
    raise ValueError(f'Stiffness not found for group {group_name} with OP {OP}')

Thrust = 1.95e6   # [N]
delta_theta = 5  # [degree]

# read from yaml file:
input_file = "inputs/lsm_input/tetra_triple_anchor_stiff_updated.yaml"
with open(input_file, 'r') as file:
    config = yaml.safe_load(file)

# Lines:
lines = []
if 'Lines' in config:
    lines_ = config['Lines']
    for line in lines_:
        group_name = line['group_name']
        scope = line['scope']
        op_data = line['OP_data']
        lines.append(Line(group_name, scope, op_data))

if 'Cells' in config:
    cells = config['Cells']
    for cell in cells:
        cell_name = cell['cell_name']
        cell_type = cell['type']
        if cell_type == 'multiple':
            units = {key: value for key, value in cell.items() if key.startswith('unit_')}
            num_units = len(units)
            K = np.zeros((num_units * 2, num_units * 2))
            i = 0  # unit index
            for unit_name, unit_data in units.items():
                j = 0  # connection index
                mooring_heading = np.radians(unit_data['mooring_heading'])
                lmg = unit_data['lmg']
                K_lines = []
                for angle, group in zip(mooring_heading, lmg):
                    # CCW is +ve
                    r = np.array([
                        [np.cos(angle), -np.sin(angle), 0, 0],
                        [np.sin(angle),  np.cos(angle), 0, 0],
                        [0, 0, np.cos(angle), -np.sin(angle)],
                        [0, 0, np.sin(angle),  np.cos(angle)]
                    ])                    
                    k = get_stiffness(lines, group, OP=0.00)
                    K_lines_i = np.matmul(np.matmul(r, k), r.transpose())
                    K_lines.append(K_lines_i)
                    if group=='shared line':
                        shared_with = unit_data['connections'][j]
                        if (shared_with - 1) > i:
                            K[2*i:2*i+2, 2*i:2*i+2] += K_lines_i[0:2, 0:2]
                            K[2*i:2*i+2, 2*(shared_with-1):2*(shared_with-1)+2] += K_lines_i[0:2, 2:4]
                            K[2*(shared_with-1):2*(shared_with-1)+2, 2*i:2*i+2] += K_lines_i[2:4, 0:2]
                            K[2*(shared_with-1):2*(shared_with-1)+2, 2*(shared_with-1):2*(shared_with-1)+2] += K_lines_i[2:4, 2:4]
                        j += 1
                    else:
                        K[2*i:2*i+2, 2*i:2*i+2] += K_lines_i[0:2, 0:2]
                i += 1

# Assume a constant, unidirectional thrust force on all turbines:
thetas = np.radians(np.arange(0, 360, delta_theta))
x, y = np.zeros((len(thetas) + 1, num_units)), np.zeros((len(thetas) + 1, num_units))
for i, aoa in enumerate(thetas):
    f = np.array([Thrust * np.cos(aoa) if j % 2 == 0 else Thrust * np.sin(aoa) for j in range(2 * num_units)]).reshape(2 * num_units, 1)
    K_inv = np.linalg.inv(K)
    zeta = K_inv @ f
    
    for j in range(num_units):
        x[i, j] = zeta[2 * j, 0]
        y[i, j] = zeta[2 * j + 1, 0]

# Close the watch circle
for j in range(num_units):
    x[-1, j] = x[0, j]
    y[-1, j] = y[0, j]

areas = np.zeros(num_units)
for j in range(num_units):
    coords = [(x[i, j], y[i, j]) for i in range(len(thetas) + 1)]
    polygon = Polygon(coords)
    areas[j] = polygon.area

# Incorporate the location of units
for j, (_, unit_data) in enumerate(units.items()):
    x[:, j] += unit_data['x']
    y[:, j] += unit_data['y']

# Plot watch circles
fig, ax = plt.subplots()
for j in range(num_units):
    ax.plot(x[:, j], y[:, j], label=f'FOWT {j+1}')

# Plot mooring lines
for _, unit_data in units.items():
    x1 = unit_data['x']
    y1 = unit_data['y']
    mooring_heading = np.radians(unit_data['mooring_heading'])
    lmg = unit_data['lmg']
    for angle, group in zip(mooring_heading, lmg):
        for line in lines:
            if line.group_name == group:
                rAnchor = line.scope
        
        x2 = x1 + rAnchor * np.cos(angle)
        y2 = y1 + rAnchor * np.sin(angle)
        ax.plot([x1, x2], [y1, y2], color='black')

ax.axis('equal')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.legend()
plt.show()

# for validation
aoa = np.radians(0)
f = np.array([Thrust * np.cos(aoa) if j % 2 == 0 else Thrust * np.sin(aoa) for j in range(2 * num_units)]).reshape(2 * num_units, 1)
K_inv = np.linalg.inv(K)
zeta = K_inv @ f
print(zeta)

import pandas as pd
df = pd.DataFrame(K)
print(df)