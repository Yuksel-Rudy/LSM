import numpy as np

class Block:
    def __init__(self, block_name, fowts, unit_cells):
        self.block_name = block_name
        self.fowts = fowts
        self.unit_cells = unit_cells
        self.bwc_x = None
        self.bwc_y = None

    def get_block_watch_circle(self, force, delta_theta, corrected):
        for _, unit_cell in self.unit_cells.items():
            unit_cell.get_cell_watch_circle(force, delta_theta, corrected=corrected)
            
        bwc_x = []
        bwc_y = []

        for fowt in self.fowts:
            cell = self.unit_cells[fowt["cell"]]
            x = cell.x
            y = cell.y

            # CCW is +ve
            unit_heading = np.radians(fowt["unit_heading"])
            r = np.array([
                [np.cos(unit_heading), -np.sin(unit_heading)],
                [np.sin(unit_heading), np.cos(unit_heading)]
            ])
            rotated_points = np.dot(r, np.vstack((x, y)))
            x_rot = rotated_points[0, :] + fowt["center_x"]
            y_rot = rotated_points[1, :] + fowt["center_y"]

            bwc_x.append(x_rot)
            bwc_y.append(y_rot)
        
        self.bwc_x = np.array(bwc_x)
        self.bwc_y = np.array(bwc_y)
