import numpy as np
import re

class Cell:
    def __init__(self, cell_name, units, lines):
        self.name = cell_name
        self.lines = lines
        num_units = len(units)
        K = np.zeros((num_units * 2, num_units * 2))
        i = 0  # unit index
        for _, unit_data in units.items():
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
                k = self.get_stiffness(group, OP=0.00)
                K_lines_i = np.matmul(np.matmul(r, k), r.transpose())
                K_lines.append(K_lines_i)
                if group=='shared line':
                    shared_with = [unit_data['connections'][j]]
                    boundary_condition = any(isinstance(item, str) and item.startswith('b') for item in shared_with)
                    if boundary_condition:
                        pattern = re.compile(r'b(\d+)')
                        b_number = [int(match.group(1)) for item in shared_with if isinstance(item, str) and (match := pattern.match(item))]
                        if len(b_number)>0:
                            shared_with_boundary = b_number[0]
                            if (shared_with_boundary - 1) > i:
                                K[2*i:2*i+2, 2*i:2*i+2] += K_lines_i[0:2, 0:2]
                                K[2*i:2*i+2, 2*(shared_with_boundary-1):2*(shared_with_boundary-1)+2] += K_lines_i[0:2, 2:4]
                                K[2*(shared_with_boundary-1):2*(shared_with_boundary-1)+2, 2*i:2*i+2] += K_lines_i[2:4, 0:2]
                                K[2*(shared_with_boundary-1):2*(shared_with_boundary-1)+2, 2*(shared_with_boundary-1):2*(shared_with_boundary-1)+2] += K_lines_i[2:4, 2:4]
                    else:
                        shared_with = shared_with[0]
                        if (shared_with - 1) > i:
                            K[2*i:2*i+2, 2*i:2*i+2] += K_lines_i[0:2, 0:2]
                            K[2*i:2*i+2, 2*(shared_with-1):2*(shared_with-1)+2] += K_lines_i[0:2, 2:4]
                            K[2*(shared_with-1):2*(shared_with-1)+2, 2*i:2*i+2] += K_lines_i[2:4, 0:2]
                            K[2*(shared_with-1):2*(shared_with-1)+2, 2*(shared_with-1):2*(shared_with-1)+2] += K_lines_i[2:4, 2:4]
                    j += 1
                else:
                    K[2*i:2*i+2, 2*i:2*i+2] += K_lines_i[0:2, 0:2]
            i += 1
        self.K = K
        self.units = units

    def get_stiffness(self, group_name, OP):
        for line in self.lines:
            if line.group_name == group_name:
                for data in line.stiffness_matrices:
                    if data['OP'] == OP:
                        return data['stiffness_matrix']
        raise ValueError(f'Stiffness not found for group {group_name} with OP {OP}')

    def get_cell_watch_circle(self, force, delta_theta):
        thetas = np.radians(np.arange(0, 360, delta_theta))
        num_units = len(self.units)
        x, y = np.zeros((len(thetas) + 1, num_units)), np.zeros((len(thetas) + 1, num_units))
        for i, aoa in enumerate(thetas):
            f = np.array([force * np.cos(aoa) if j % 2 == 0 else force * np.sin(aoa) for j in range(2 * num_units)]).reshape(2 * num_units, 1)
            K_inv = np.linalg.inv(self.K)
            zeta = K_inv @ f
            
            for j in range(num_units):
                x[i, j] = zeta[2 * j, 0]
                y[i, j] = zeta[2 * j + 1, 0]

        # Close the watch circle
        for j in range(num_units):
            x[-1, j] = x[0, j]
            y[-1, j] = y[0, j]            

        self.x = x
        self.y = y