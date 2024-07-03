import numpy as np

class LinearModel:
    def __init__(self, inline_stiffness, transverse_stiffness, shared_inline_stiffness, shared_transverse_stiffness, mooring_heading, shared_status) -> None:
        self.inline_stiffness = inline_stiffness
        self.transverse_stiffness = transverse_stiffness
        self.shared_inline_stiffness = shared_inline_stiffness
        self.shared_transverse_stiffness = shared_transverse_stiffness        
        self.mooring_heading = mooring_heading
        self.shared_status = shared_status
        self.K_local = np.array([
            [self.inline_stiffness, 0],
            [0, self.transverse_stiffness]
        ])
        self.Ks_local = np.array([
            [self.shared_inline_stiffness, 0],
            [0, self.shared_transverse_stiffness]
        ])
        
        # Create an R for each mooring line and store in a list
        self.R_matrices = []
        for angle in mooring_heading:
            R = np.array([
                [np.cos(angle), np.sin(angle)],
                [-np.sin(angle), np.cos(angle)]
            ])
            self.R_matrices.append(R)
        self.K_lines, self.C_lines = self.compute_K_line()

    def compute_K_line(self):
        K_lines = []
        C_lines = []
        for i, R in enumerate(self.R_matrices):
            if self.shared_status[i]:
                K_line = R @ self.Ks_local @ R.T
            else:
                K_line = R @ self.K_local @ R.T

            C_line = np.ones_like(K_line, dtype=float)
            K_lines.append(K_line)
            C_lines.append(C_line)
        return K_lines, C_lines
    
    def compute_C_line(self, Kn_lines):
        C_lines = []
        for K_line, Kn_line in zip(self.K_lines, Kn_lines):
            non_zero_mask = K_line != 0
            C_line = np.ones_like(K_line, dtype=float)
            C_line[non_zero_mask] = np.divide(Kn_line[non_zero_mask], K_line[non_zero_mask])
            C_lines.append(C_line)
        self.C_lines = C_lines
    def correct_K_line(self):
        corrected_K_lines = []
        for K_line, C_line in zip(self.K_lines, self.C_lines):
            corrected_K_line = np.multiply(K_line, C_line)
            corrected_K_lines.append(corrected_K_line)
        return corrected_K_lines