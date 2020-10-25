# DE2 Computing 2 Coursework: Tetriling with missing pieces
# Name: Louis Horrell
# CID: 01358733

'''
Code consists of two main solver classes (GreedySolver and RecuSolver)

GreedySolver method summary:
    - Scan the target matrix from top - bottom, left - right
    - Stop when a 1 is reached
    - Find all shapes that can fit at that location
    - Score the shapes based on how many immediate neighbours they have in the target
    - Pick the minimum scoring shape (ties are broken arbitrarily) and fit it
    - Continue through the matrix, fitting a shape wherever possible
    - After the 1st pass, the target is scanned again
    - Shapes with 75% coverage (3 out of 4 tiles) are force fitted, to maximise solution accuracy
    - This approach is greedy in that it fits the best tile available at each position, without regard for future consequences

RecuSolver method summary:
    - Scan the target for a 1
    - Fit the best fitting shape at that location
    - Recursively try to complete the remaining target of n-1 shapes
    - If a solution is impossible, backtrack one level, and try another shape
    - If a solution is still impossible, backtrack again
    - Continue with this brute-force approach until a perfect solution is found

Due to the brute-force nature of the recursive (RecuSolver) approach, it is only used for small grids (of less than 100 elements).
For anything larger, the much more efficient, but invariably imperfect greedy approach is used
'''

class Tetromino:
    '''
    The Tetromino class stores data for each of the 16 valid pieces
    self.footprint stores the position of each tile of the tetromino relative to it's root
    self.outline_path stores the position of the neighbouring target elements relative to the root 
    '''
    def __init__(self, footprint):
        self.footprint = [(0, 0)] + footprint           # (0, 0) is the root position for all Tetrominos
        self.outline_path = self.find_outline_path()

    def find_outline_path(self):
        path = []
        for p in self.footprint:                    # For each position, p, in self.footprint
            NSEW = [                                # Find its neighbours to the North, South, East and West
                (p[0] - 1, p[1]),
                (p[0] + 1, p[1]),
                (p[0], p[1] + 1),
                (p[0], p[1] - 1)
            ]
            for d in NSEW:                          # For each direction, d, in NSEW
                if d in self.footprint:             # If the direction is already in self.footprint, move on
                    continue
                if d == (0, -1) or d == (-1, 0):    # Path elements to the N and W of the root are also removed since they are guaranteed...
                    continue                        # ... to be filled already, or impossible to fill (reduces checking workload by 20%)
                path.append(p)
        return path


class Solver:
    piece_id = 0

    position_eval_data = [
        [(1, 0), {4, 5, 7, 8, 10, 11, 12, 13, 14, 16, 17, 19}],     # The tuple in each array specifies a relative postion from a root
        [(0, 1), {6, 7, 9, 10, 15, 16, 18}],                        # The set of shape_ids in each array can be eliminated if the target...
        [(1, 1), {6, 11, 12, 13, 15, 17, 18}],                      # ... is empty, or already tiled at that point
        [(1, -1), {5, 13, 14, 16, 19}],
        [(2, 0), {4, 8, 10, 12, 14}],
        [(0, 2), {7, 9, 15}],
        [(1, 2), {9, 11, 18}],
        [(2, 1), {4, 6, 17}],
        [(2, -1), {8, 19}],
        [(1, -2), {5}]
    ]

    shapes = {
        4: Tetromino([(1, 0), (2, 0), (2, 1)]),         # Instances of the Tetromino class for each shape ID
        5: Tetromino([(1, -2), (1, -1), (1, 0)]),
        6: Tetromino([(0, 1), (1, 1), (2, 1)]),
        7: Tetromino([(0, 1), (0, 2), (1, 0)]),
        8: Tetromino([(1, 0), (2, -1), (2, 0)]),
        9: Tetromino([(0, 1), (0, 2), (1, 2)]),
        10: Tetromino([(0, 1), (1, 0), (2, 0)]),
        11: Tetromino([(1, 0), (1, 1), (1, 2)]),
        12: Tetromino([(1, 0), (1, 1), (2, 0)]),
        13: Tetromino([(1, -1), (1, 0), (1, 1)]),
        14: Tetromino([(1, -1), (1, 0), (2, 0)]),
        15: Tetromino([(0, 1), (0, 2), (1, 1)]),
        16: Tetromino([(0, 1), (1, -1), (1, 0)]),
        17: Tetromino([(1, 0), (1, 1), (2, 1)]),
        18: Tetromino([(0, 1), (1, 1), (1, 2)]),
        19: Tetromino([(1, -1), (1, 0), (2, -1)]),
    }
    
    '''Lines 97 - 137 contain methods used and inherited by both the GreedySolver and RecuSolver subclasses'''

    def __init__(self, T):
        T = [[None, None] + r + [None, None] for r in T]        # Pad the target with None values, to avoid special treatment of edge pieces 
        self.cols = len(T[0])                                   # Numpy.pad() not compatible with NoneType, hence not used
        row_pad = [None for c in range(self.cols)]              # NoneType used for performance reasons (see line 129)
        self.T = [row_pad, row_pad] + T + [row_pad, row_pad]
        self.rows = len(self.T)
        self.S = [[(0, 0) for c in range(self.cols)] for r in range(self.rows)]     # Initialise solution matrix of (0, 0) tuples

    def find_shapes(self, i, j):
        '''
        Function checks the target in various positions around the root at (i, j)
        self.position_eval_data is used to elimate shapes if the element in the target is empty, or filled already
        '''
        valid_set = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}      # Initially assume all shapes will fit
        for p in self.position_eval_data:               # For each position, p, in position_eval_data
            if not self.T[i + p[0][0]][j + p[0][1]]:    # If the element is None (already filled) or 0 (should not be filled)
                valid_set = valid_set - p[1]            # Remove those shapes from the valid_set
        return valid_set

    def find_shape_cost(self, i, j, shape_id):
        ''' 
        Function works around a specified shape's outline_path, with the root at (i, j) in the target matrix
        1 is added to the cost if the target element has a value of 1
        The most efficient shape at this location is (usually) that with the minimum cost
        '''
        cost = 0
        for p in self.shapes[shape_id].outline_path:
            if self.T[i + p[0]][j + p[1]]:
                cost += 1
        return cost

    def fit_shape(self, i, j, shape_id):
        '''
        Function places a tile in the solution matrix, and sets the target to None where the shape has been placed
        None is used for filled elements in preference to 0 as it allows for differentiation during the force fitting stage (see line 172)
        None is used in preference to e.g. -1 as it preserves truthy/falsy conditional operators, significantly improving performance
        '''
        self.piece_id += 1
        for el in self.shapes[shape_id].footprint:
            self.S[i + el[0]][j + el[1]] = (shape_id, self.piece_id)
            self.T[i + el[0]][j + el[1]] = None


class GreedySolver(Solver):
    def solve(self):
        for i in range(2, self.rows - 2):                   # Iterate through target matrix
            for j in range(2, self.cols - 2):
                if not self.T[i][j]:                        # If target is zero or already filled, move on
                    continue
                valid_set = self.find_shapes(i, j)
                if not valid_set:                           # If no shapes fit, move on
                    continue
                min_cost_shape_id = self.find_min_cost_shape(i, j, valid_set)
                self.fit_shape(i, j, min_cost_shape_id)     # Fit the minimum cost shape
        for i in range(2, self.rows - 2):                   # Force fit pass
            for j in range(2, self.cols - 2):
                if not self.T[i][j]:
                    continue
                ff_shape_id = self.find_force_fit_shape(i, j)
                if ff_shape_id:
                    self.fit_shape(i, j, ff_shape_id)
        self.S = [row[2:-2] for row in self.S[2:-2]]        # Remove padding from solution matrix and return
        return self.S

    def find_min_cost_shape(self, i, j, valid_set):
        '''Takes in a set of shapes that fit at a given location in the target, and returns the minimum cost shape ID'''
        min_cost, min_cost_shape_id = 10, None
        for shape_id in valid_set:
            cost = self.find_shape_cost(i, j, shape_id)
            if cost < min_cost:
                min_cost, min_cost_shape_id = cost, shape_id
        return min_cost_shape_id

    def find_force_fit_shape(self, i, j):
        '''Finds shapes with 75% coverage in the target to maximise solution accuracy'''
        valid_set = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}
        for p in self.position_eval_data:
            if self.T[i + p[0][0]][j + p[0][1]] is None:    # If the target has a value of None, a shape is already present in the solution
                valid_set = valid_set - p[1]
        for shape_id in valid_set:
            score = 0
            for p in self.shapes[shape_id].footprint:
                if self.T[i + p[0]][j + p[1]]:              # If the position, p, in the shape's footprint falls on a 1, add one to score
                    score += 1
            if score == 3:                                  # If a shape has 3 out of 4 tiles on 1s in the target, return it for placing
                return shape_id
        return None


class RecuSolver(Solver):
    def solve(self):                                        # Calls the recursive function, and awaits a solution
        self.recurse()
        self.S = [row[2:-2] for row in self.S[2:-2]]        # Remove padding from solution matrix and return
        return self.S

    def recurse(self):
        for i in range(2, self.rows - 2):                   # Iterate through the target
            for j in range(2, self.cols - 2):
                if not self.T[i][j]:                        # If target is zero or already filled, move on
                    continue
                valid_set = self.find_shapes(i, j)          # Find shapes that fit
                costed_shapes_array = self.find_costed_array(i, j, valid_set)   # Try the minimum cost shapes first (see line XX)
                for cost_tuple in costed_shapes_array:      # For each shape that fits
                    self.fit_shape(i, j, cost_tuple[0])     # Place it...
                    if self.recurse():                      # Try and solve the remaining problem (with n-1 shapes)
                        return True
                    else:
                        self.backtrack(i, j, cost_tuple[0]) # backtrack 1 level (remove the shape and try the next in costed_shapes_array)
                return False                                # No shapes fit
        return True                                         # No 1s remain

    def backtrack(self, i, j, shape_id):
        '''Removes a shape from the target if recursion fails'''
        self.piece_id -= 1
        for p in self.shapes[shape_id].footprint:
            self.S[i + p[0]][j + p[1]] = (0, 0)
            self.T[i + p[0]][j + p[1]] = 1

    def find_costed_array(self, i, j, valid_set):
        '''
        Sorts the set of valid shapes in order of ascending cost
        The minimum cost shapes are then tried first in the recursion
        This does not improve the worst case O(n) running time, but significantly improves the expected running time
        '''
        costed_shapes_array = []
        for shape_id in valid_set:
            cost_tuple = (shape_id, self.find_shape_cost(i, j, shape_id))
            costed_shapes_array.append(cost_tuple)
        costed_shapes_array.sort(key=lambda cost_tuple: cost_tuple[1])
        return costed_shapes_array


def Tetris(T):
    height = len(T)
    width = len(T[0])
    if height * width <= 100:       # For small problems, solve recursively
        solver = RecuSolver(T)
    else:                           # Otherwise, solve with greedy approach
        solver = GreedySolver(T)
    return solver.solve()
