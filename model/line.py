import numpy as np

class Line:
    def __init__(self, group_name, scope, OP_data):
        self.group_name = group_name
        self.scope = scope
        self.OP_data = OP_data
        self.stiffness_matrices = []

        for data in OP_data:
            OP = data['OP']
            k_l = data['k_l']
            k_t = data['k_t']

            stiffness_matrix = np.array([
                [k_l, 0],
                [0, k_t]
            ])

            self.stiffness_matrices.append({
                'OP': OP,
                'stiffness_matrix': stiffness_matrix
            })
