import concurrent.futures
import inspect
import logging
import math
import os
from datetime import datetime
from typing import Callable, Tuple, Optional, get_type_hints

from magiccube import Cube
from magiccube.cube_base import CubeException
from magiccube.solver.basic.basic_solver import BasicSolver

from bot.config import TIME_LIMIT, CUBE_SIZE
from bot.judge.example import Solver as ExampleSolver

class Status:
    AC = 0
    WA = 1
    TLE = 2
    RE = 3
    CE = 4


class Judge:
    """Judge class to handle the judging process."""
    
    ranklist = {}
    time = 0
    steps = 0
    max_steps = 0
    cube = Cube(CUBE_SIZE)
    
    @classmethod
    def init(cls) -> None:
        """Initialize the Judge class."""
        
        cls.logger = logging.getLogger(__name__)
        
        # Test cases
        cls.test_cases: list = []
        
        for _ in range(10):
            cube = Cube(CUBE_SIZE)
            cls.test_cases.append(cube.generate_random_moves(20))
            

    @classmethod
    def judge(cls, file: bytes, data: bytes) -> Tuple[int, str]:
        """Judge the file and return the status code and message."""
        
        # File
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
        
        if not os.path.exists(path):
            os.makedirs(path)
        
        file_path = os.path.join(path, "__init__.py")
        data_path = os.path.join(path, "param.json")
        
        with open(file_path, "wb") as f:
            f.write(file)
            
        with open(data_path, "wb") as f:
            f.write(data)
            
        # Compile Error   
        try:
            from bot.judge.test import Solver
            
        except ImportError as e:
            cls.logger.error(f"ImportError: {e}")
            return Status.CE, "ImportError: {}".format(e)
        
        except SyntaxError as e:
            cls.logger.error(f"SyntaxError: {e}")
            return Status.CE, "SyntaxError: {}".format(e)
        
        except AttributeError as e:
            cls.logger.error(f"AttributeError: {e}")
            return Status.CE, "AttributeError: {}".format(e)
        
        if not isinstance(Solver, type(ExampleSolver)):
            cls.logger.error(f"The type of Solver is {type(Solver)}, but it should be {type(ExampleSolver)}")
            return Status.CE, "The type of Solver is {}, but it should be {}".format(type(Solver), type(ExampleSolver))
        
        for attr in ["solve"]:
            if not hasattr(Solver, attr):
                cls.logger.error(f"Solver does not have {attr} method")
                return Status.CE, f"Solver does not have {attr} method"
            
            func = getattr(Solver, attr)
            if not isinstance(func, Callable):
                cls.logger.error(f"{attr} is not Callable")
                return Status.CE, f"{attr} is not Callable"
            
            sig = inspect.signature(func)
            example_sig = inspect.signature(getattr(ExampleSolver, attr))
            hints = get_type_hints(func)
            example_hints = get_type_hints(getattr(ExampleSolver, attr))
            
            for (param_name, param), (example_param_name, example_param) in zip(sig.parameters.items(), example_sig.parameters.items()):
                
                param_type = hints.get(param_name, None)
                example_param_type = example_hints.get(example_param_name, None)
                
                if param_name != example_param_name:
                    cls.logger.error(f"{param_name} does not match {example_param_name}")
                    return Status.CE, f"{param_name} does not match {example_param_name}"
                
                if param_type is None:
                    cls.logger.error(f"{param_name} has no type hint")
                    return Status.CE, f"{param_name} has no type hint"
                
                if param_type != example_param_type:
                    cls.logger.error(f"{param_name} type hint does not match")
                    return Status.CE, f"{param_name} type hint does not match"
                
                if param.default is not param.empty:
                    cls.logger.error(f"{param_name} has a default value")
                    return Status.CE, f"{param_name} has a default value"
                
        status = cls.test(Solver.solve)
        
        return status
    
    
    @classmethod
    def runner(cls, func: Callable, *args, **kwargs) -> Optional[Tuple[str, float]]:
        """Run the function and return the status code and message."""
         
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            
            try:
                start_time = datetime.now()
                result = future.result(timeout=TIME_LIMIT)
                end_time = datetime.now()
                elapsed_time = (end_time - start_time).total_seconds()  
                return result, elapsed_time
            
            except concurrent.futures.TimeoutError:
                raise TimeoutError("Time Limit Exceeded")
        
        
    @classmethod
    def test(cls, func: Callable) -> Tuple[int, str]:
        """Test the function and return the status code and message."""
        
        total_time = 0
        total_steps = 0
        total_max_steps = 0
        
        # Test cases
        for idx, test_case in enumerate(cls.test_cases):
            
            cube = Cube(CUBE_SIZE)
            cube.rotate(test_case)
            cls.cube.rotate(test_case)
            total_max_steps += len(BasicSolver(cls.cube).solve())
            
            try:
                test_cube = Cube(CUBE_SIZE)
                test_cube.rotate(test_case)
                output = cls.runner(func, test_cube)
                
                if output is None:
                    return Status.WA, f"Wrong Answer in test case {idx + 1}"
                
                result, elapsed_time = output
                total_time += elapsed_time
                
                if not isinstance(result, str):
                    return Status.WA, f"Wrong Answer in test case {idx + 1}: result is {type(result)}, but it should be str"
                
                cls.logger.debug(cube)
                cube.rotate(result)
                cls.logger.debug(f"Test case {idx + 1}: \ntest_case: {test_case}\nresult: ({result})\ncube: {cube}\nelapsed time: {elapsed_time:.2f}s")
                total_steps += len(result.split())
                
                if not cube.is_done():
                    return Status.WA, f"Wrong Answer in test case {idx + 1}: cube is not solved"
                
            except CubeException as e:
                return Status.WA, f"Wrong Answer in test case {idx + 1}: {e}"
                
            except TimeoutError:
                return Status.TLE, f"Time Limit Exceeded in test case {idx + 1}"
            
            except Exception as e:
                return Status.RE, f"Runtime Error in test case {idx + 1}: {e}"
            
        cls.time = total_time
        cls.steps = total_steps
        cls.max_steps = total_max_steps
            
        return Status.AC, f"Accepted {len(cls.test_cases)} test cases, time: {total_time:.2f}s, steps: {total_steps:.2f}"
    
    
    @classmethod
    def record(cls, username: str) -> None:
        """Record the score."""
        
        def score() -> float:
            """Calculate the score."""
            return math.exp(-cls.time / TIME_LIMIT) * 50 + math.exp(-cls.steps / cls.max_steps) * 50
        
        if username not in cls.ranklist:
            cls.ranklist[username] = score()
            
        elif cls.ranklist[username] > score():
            cls.ranklist[username] = score()
        
        cls.ranklist = dict(sorted(cls.ranklist.items(), key=lambda item: item[1]))
        
        
    @classmethod
    def reset(cls) -> None:
        """Reset the Judge class."""
        
        cls.time = 0
        cls.steps = 0
        cls.max_steps = 0
        cls.cube.reset()