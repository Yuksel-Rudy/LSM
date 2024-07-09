import matplotlib.pyplot as plt
from famodel.project import Project
import moorpy as mp
import numpy as np

Array = Project(file='inputs/fam_inputs/4trtles_ont.yaml', raft=0)
Array.getMoorPyArray(cables=0,plt=0)
Array.ms.plot()
plt.show()