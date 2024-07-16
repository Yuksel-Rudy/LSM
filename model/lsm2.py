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
        self.unit_cells = []

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
                units = {key: value for key, value in cell.items() if key.startswith('unit_')}
                self.unit_cells.append(Cell(cell_name, units, self.lines))

    
    def plot_wc(self, ax, force, delta_theta, color="blue", label="watch circle", anchor_and_mooring=True):
        for cell in self.unit_cells:
            num_units = len(cell.units)
            cell.get_cell_watch_circle(force, delta_theta)
            x = cell.x
            y = cell.y
            ii = 0
            for j, (_, unit_data) in enumerate(cell.units.items()):
                x1 = unit_data['x']
                y1 = unit_data['y']
                ax.plot(x[:, j] + x1, y[:, j] + y1, color=color, label=label if j == 0 else None)
                ax.text(np.mean(x[:, j]) + x1, np.mean(y[:, j]) + y1, f'P{j+1}', fontsize=12, ha='right')                
                mooring_heading = np.radians(unit_data['mooring_heading'])
                lmg = unit_data['lmg']
                if anchor_and_mooring:
                    for angle, group in zip(mooring_heading, lmg):
                        for line in self.lines:
                            if line.group_name == group:
                                rAnchor = line.scope
                        
                        x2 = x1 + rAnchor * np.cos(angle)
                        y2 = y1 + rAnchor * np.sin(angle)
                        ax.plot([x1, x2], [y1, y2], color='black')
                    
                        if group=='anchored line':
                            ax.scatter(x2, y2, color='red', marker='x', label='anchor' if ii == 0 else None)
                            ii += 1

            ax.axis('equal')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')