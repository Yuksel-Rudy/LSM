import numpy as np

class Cell:
    def __init__(self, cell_name, mooring_heading, lmg, lines):
        self.name = cell_name
        self.mooring_heading = mooring_heading
        self.lmg = lmg
        self.lines = lines
        Ri = []
        Ki = []
        for angle, group in zip(mooring_heading, lmg):
            # CCW is +ve
            r = np.array([
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle),  np.cos(angle)]
            ])
            k = self.get_stiffness(group, OP=0.00)
            Ri.append(r)
            Ki.append(k)
        self.Ri = Ri
        self.Ki = Ki
        self.compute_K_line()
        self.K = sum(self.K_lines)

    def get_stiffness(self, group_name, OP):
        for line in self.lines:
            if line.group_name == group_name:
                for data in line.stiffness_matrices:
                    if data['OP'] == OP:
                        return data['stiffness_matrix']
        raise ValueError(f'Stiffness not found for group {group_name} with OP {OP}')
    
    def compute_K_line(self):
        K_lines = []
        C_lines = []
        R = self.Ri
        K = self.Ki
        for r, k in zip(R, K):
            K_line = r @ k @ r.T
            C_line = np.ones_like(K_line, dtype=float)
            K_lines.append(K_line)
            C_lines.append(C_line)
        self.K_lines = K_lines
        self.C_lines = C_lines
    
    def lin2nonlin_corr(self, Kn_lines):
        K_lines = self.K_lines
        C_lines = []
        corrected_K_lines = []
        for K_line, Kn_line in zip(K_lines, Kn_lines):
            non_zero_mask = K_line != 0
            C_line = np.ones_like(K_line, dtype=float)
            C_line[non_zero_mask] = np.divide(Kn_line[non_zero_mask], K_line[non_zero_mask])
            C_lines.append(C_line)
        
        for K_line, C_line in zip(K_lines, C_lines):
            corrected_K_line = np.multiply(K_line, C_line)
            corrected_K_lines.append(corrected_K_line)

        self.K_c = sum(corrected_K_lines)

    def get_cell_watch_circle(self, force, delta_theta, corrected):
        if corrected:
            K = self.K_c
        else:
            K = self.K
        
        thetas = np.radians(np.arange(0, 360, delta_theta))
        x, y = [], []
        for aoa in thetas:  # aoa: angle of attach
            f = np.array([[force * np.cos(aoa)],[force * np.sin(aoa)]])
            zeta = np.linalg.inv(K) @ f
            x.append(zeta[0][0])
            y.append(zeta[1][0])
        
        x.append(x[0])
        y.append(y[0])        
        self.x = x
        self.y = y