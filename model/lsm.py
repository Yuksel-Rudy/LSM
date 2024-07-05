import numpy as np
import yaml
from .line import Line
from .cell import Cell
from .block import Block

class LinearModel:
    def __init__(self, input_file):
        with open(input_file, 'r') as file:
            config = yaml.safe_load(file)
        
        self.lines = []
        self.unit_cells = {}
        self.blocks = {}
        self.array = []

        # Lines:
        if 'Lines' in config:
            lines = config['Lines']
            for line in lines:
                group_name = line['group_name']
                op_data = line['OP_data']
                self.lines.append(Line(group_name, op_data))

        # Cells:
        if 'Cells' in config:
            cells = config['Cells']
            for cell in cells:
                cell_name = cell['cell_name']
                mooring_heading = np.radians(cell['mooring_heading'])
                lmg = cell['lmg']
                self.unit_cells[cell_name] = Cell(cell_name, mooring_heading, lmg, self.lines)

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

    def get_array_watch_circle(self, force, delta_theta, corrected=False):
        bwc_x, bwc_y = [], []  # all block watch circles together 
        awc_x, awc_y = [], []  # all array watch circles together
        
        for _, block in self.blocks.items():
            block.get_block_watch_circle(force, delta_theta, corrected=corrected)
            
            x = block.bwc_x
            y = block.bwc_y

            bwc_x.append(x)
            bwc_y.append(y)

        for block in self.array:
            # CCW is +ve
            unit_heading = np.radians(block["unit_heading"])
            r = np.array([
                [np.cos(unit_heading), -np.sin(unit_heading)],
                [np.sin(unit_heading), np.cos(unit_heading)]
            ])

            x_rot_all, y_rot_all = [], []
            for x, y in zip(bwc_x, bwc_y):
                rotated_points = np.dot(r, np.vstack((x.flatten(), y.flatten())))
                x_rot = rotated_points[0, :] + block["center_x"]
                y_rot = rotated_points[1, :] + block["center_y"]
                x_rot = x_rot.reshape(x.shape)
                y_rot = y_rot.reshape(y.shape)

                x_rot_all.append(x_rot)
                y_rot_all.append(y_rot)

            awc_x.append(x_rot)
            awc_y.append(y_rot)
            
        awc_x = np.array(awc_x, dtype=object)
        awc_y = np.array(awc_y, dtype=object)
        
        return awc_x, awc_y