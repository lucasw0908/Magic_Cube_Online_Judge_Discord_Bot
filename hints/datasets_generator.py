import os
import json

import numpy as np
from magiccube import Cube
from magiccube.solver.basic.basic_solver import BasicSolver


COLOR_CODE = {
    "R": 0.0,
    "O": 0.2,
    "W": 0.4,
    "Y": 0.6,
    "B": 0.8,
    "G": 1.0
}

MOVE_CODE = {
    "U": 0,
    "D": 1,
    "L": 2,
    "R": 3,
    "F": 4,
    "B": 5,
    "U'": 6,
    "D'": 7,
    "L'": 8,
    "R'": 9,
    "F'": 10,
    "B'": 11
}

x_trains = []
y_trains = []
data_count = 100

for i in range(data_count):
    cube = Cube(3)
    cube.scramble(20)
    solver = BasicSolver(cube)
    solution = solver.solve()
    
    x_train = []
    
    for step in solution:
        output = []
        for Coordinates, CubePiece in cube.get_all_pieces().items():
            output.extend([COLOR_CODE[s] for s in CubePiece.get_piece_colors_str()])
        x_train.append(np.array(output).reshape(-1))
        
    x_train = np.array(x_train).reshape(-1, 54)
    y_train = np.array([np.eye(len(MOVE_CODE))[MOVE_CODE[str(s)]] for s in solution]).reshape(-1, len(MOVE_CODE))
    
    x_trains.extend(x_train)
    y_trains.extend(y_train)
    
    print(f"{i + 1}/{data_count} data generated.")
    
    
with open(os.path.join(os.path.dirname(__file__), "train.json"), "wb") as f:
    
    class NumpyArrayEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return json.JSONEncoder.default(self, obj)
        
    f.write(json.dumps({
        "x_train": x_trains,
        "y_train": y_trains
    }, cls=NumpyArrayEncoder).encode("utf-8"))
    
    
print("Data generated successfully.")
print(f"Data count: {len(x_trains)}")