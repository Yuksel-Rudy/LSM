import numpy as np
import yaml
from .line import Line
from .cell import Cell
from .block import Block
import matplotlib.pyplot as plt

class LinearModel:
    def __init__(self, input_file):
        with open(input_file, 'r') as file:
            config = yaml.safe_load(file)
        
        self.lines = []
        self.unit_cells = {}
        self.blocks = {}
        self.array = []
        self.awc_x = []
        self.awc_y = []
        self.turbine_x = []
        self.turbine_y = []
        # Lines:
        if 'Lines' in config:
            lines = config['Lines']
            for line in lines:
                group_name = line['group_name']
                scope = line['scope']
                op_data = line['OP_data']
                self.lines.append(Line(group_name, scope, op_data))

        # Cells:
        if 'Cells' in config:
            cells = config['Cells']
            for cell in cells:
                cell_name = cell['cell_name']
                cell_type = cell['type']
                mooring_heading = np.radians(cell['mooring_heading'])
                lmg = cell['lmg']
                self.unit_cells[cell_name] = Cell(cell_name, cell_type, mooring_heading, lmg, self.lines)

        # Blocks:
        if 'Blocks' in config:
            blocks = config['Blocks']
            for block in blocks:
                block_name = block['block_name']
                fowts = block['fowts']
                self.blocks[block_name] = Block(block_name, fowts, self.unit_cells)

        # Arrays: 
        if 'Array' in config:
            array = config['Array']
            for array_block in array:
                self.array.append(array_block)

    def get_array_watch_circle(self, force, delta_theta, corrected=False, magnify_watch_circle=1):
        bt_x, bt_y = [], [] # all block wind turbine coordinates together
        at_x, at_y = [], [] # all array wind turbine coordinates together
        bwc_x, bwc_y = [], []  # all block watch circles together 
        awc_x, awc_y = [], []  # all array watch circles together
        
        for _, block in self.blocks.items():
            block.get_block_watch_circle(force, delta_theta, corrected, magnify_watch_circle)
            
            x = block.bwc_x
            y = block.bwc_y

            bwc_x.append(x)
            bwc_y.append(y)

            turbine_x = block.turbine_x
            turbine_y = block.turbine_y

            bt_x.append(turbine_x)
            bt_y.append(turbine_y)

        for i, block in enumerate(self.array):
            # CCW is +ve
            unit_heading = np.radians(block["unit_heading"])
            r = np.array([
                [np.cos(unit_heading), -np.sin(unit_heading)],
                [np.sin(unit_heading), np.cos(unit_heading)]
            ])

            x_rot_all, y_rot_all = [], []
            block_idx = next((idx for idx, key in enumerate(self.blocks) if key == block["name"]), None)
            for x, y in zip(bwc_x[block_idx], bwc_y[block_idx]):
                rotated_points = np.dot(r, np.vstack((x.flatten(), y.flatten())))
                x_rot = rotated_points[0, :] + block["center_x"]
                y_rot = rotated_points[1, :] + block["center_y"]
                x_rot = x_rot.reshape(x.shape)
                y_rot = y_rot.reshape(y.shape)

                x_rot_all.append(x_rot)
                y_rot_all.append(y_rot)

            awc_x.append(x_rot_all)
            awc_y.append(y_rot_all)
            
            x_rot_all, y_rot_all = [], []
            for x, y in zip(bt_x[block_idx], bt_y[block_idx]):
                rotated_points = np.dot(r, np.vstack((x.flatten(), y.flatten())))
                x_rot = rotated_points[0, :] + block["center_x"]
                y_rot = rotated_points[1, :] + block["center_y"]
                x_rot = x_rot.reshape(x.shape)
                y_rot = y_rot.reshape(y.shape)

                x_rot_all.append(x_rot)
                y_rot_all.append(y_rot)

            at_x.append(x_rot_all)
            at_y.append(y_rot_all)
            
        awc_x = np.array(awc_x, dtype=object)
        awc_y = np.array(awc_y, dtype=object)
        
        at_x = np.array(at_x, dtype=object)
        at_y = np.array(at_y, dtype=object)
        self.awc_x = awc_x
        self.awc_y = awc_y
        self.turbine_x = at_x
        self.turbine_y = at_y
        return awc_x, awc_y
    
    def plot(self, labels=False):
        fig, ax = plt.subplots()
        for i, block in enumerate(self.array):
            block_unit_heading = np.radians(block["unit_heading"])
            for j, fowt in enumerate(self.blocks[block['name']].fowts):
                fowt_unit_heading = np.radians(fowt["unit_heading"])
                cell = self.unit_cells[fowt["cell"]]
                x1 = self.turbine_x[i][j]
                y1 = self.turbine_y[i][j]
                for k, (an, group) in enumerate(zip(cell.mooring_heading, cell.lmg)):
                    for line in self.lines:
                        if line.group_name == group:
                            rAnchor = line.scope
                    
                    angle = an + fowt_unit_heading + block_unit_heading
                    x2 = x1 + rAnchor * np.cos(angle)
                    y2 = y1 + rAnchor * np.sin(angle)
                    plt.plot([x1, x2], [y1, y2], color='black', label='mooring line' if i==0 and j==0 and k==0 and labels else None, zorder=1)
                    plt.scatter(x2, y2, color='green', label='anchor' if i==0 and j==0 and k==0 and labels else None, zorder=2)
                
                plt.scatter(x1, y1, color='blue', label='wind turbine' if i==0 and j==0 and labels else None, zorder=3)
                plt.plot(self.awc_x[i][j], self.awc_y[i][j], color='red', label='watch circle' if i==0 and j==0 and labels else None, zorder=4)
        
        plt.axis('equal')
        plt.xlabel('x-coordinate')
        plt.ylabel('y-coordinate')
        return fig, ax