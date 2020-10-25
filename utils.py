# ####################################################
# DE2-COM2 Computing 2
# Individual project
#
# Title: UTILS
# Authors: Liuqing Chen, Feng Shi, Isaac Engel, and
#          Nicolas Rojas
# ####################################################

# ------ Please make sure you have installed the following packages: matplotlib, numpy, PIL -------

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageDraw
import operator
import random

"""
 ------------------------------- MAIN UTIL FUNCTIONS ------------------------------- 
 The functions below are used in the performance test. They are useful tools that 
 may help you to test your algorithm. They are the following:
 
    check_solution(target, solution, forbidden_pieces): checks if a solution is valid
    
    generate_target(width, height, density, forbidden_pieces): generates a random solvable target shape
    
    visualisation(target, solution, forbidden_pieces): displays the target vs the solution
    
    visual_perfect(perfect, solution, forbidden_pieces): displays the perfect_solution vs the solution
    
"""


def check_solution(target, solution, forbidden_pieces):
    """
    Check if a solution is valid
    :param target: target shape
    :param solution: student's solution
    :param forbidden_pieces: set of forbidden shapeIDs 
    :return: valid: True or False
    :return: missing: number of missing blocks
    :return: excess: number of excess blocks
    :return: error_pieces: list of wrongly labelled pieces
    """

    valid = True
    missing, excess = boundary_check(target, solution)
    error_pieces = checkshape(solution, forbidden_pieces)

    if missing is None or excess is None or error_pieces is None:
        error_pieces = []
        valid = False  
    elif len(error_pieces) > 0 :
        valid = False  
        print(error_pieces)

    return valid, missing, excess, error_pieces


def generate_target(width, height, density, forbidden_pieces):
    """
    Generates a random solvable target shape
    NOTE: this function may not be able to generate targets with density above 0.8, so it is
    recommended to keep it below that value.
    :param width: number of columns of the target (must be positive)
    :param height: number of rows of the target (must be positive)
    :param density: number of columns of the target (must be between 0 and 1, recommended < 0.8)
    :param forbidden_pieces: set of forbidden shapeIDs
    """
    assert width > 0, "width must be a positive integer"
    assert height > 0, "height must be a positive integer"
    assert 0 <= density <= 1, "density must be a number between 0 and 1"
    size = width * height
    nblocks = size * density
    npieces, _ = divmod(nblocks, 4)
    npieces = int(npieces)
    target = [[0] * width for row in range(0, height)]
    solution = [[(0,0) for col in range(0, width)] for row in range(0, height)]
    piece_id = 0 # record piece_id 
    for count in range(0, npieces):
        valid_piece = False
        end_counter = 0
        
        while not valid_piece and end_counter < 1000:
            r = random.randint(0, height-1)
            c = random.randint(0, width -1)
            valid_shapes = list(set(range(1,20)) - forbidden_pieces)
            random_index = random.randint(0,len(valid_shapes)-1)
            shape_id = valid_shapes[random_index]
            
            shape = generate_shape(shape_id)
            piece = [[y + r, x + c] for [y, x] in shape]
            valid_piece = check_if_piece_is_valid(piece, target)
            if valid_piece:
                piece_id += 1
                for [r, c] in piece:
                    target[r][c] = 1                
                    solution[r][c] = (shape_id,piece_id)
            end_counter += 1
    return target, solution


def visualisation(target, solution, forbidden_pieces):
    """
    Displays the target vs the solution
    :param target: target shape
    :param solution: student's solution
    :param forbidden_pieces: set of forbidden shapeIDs 
    """
    wrong_list = checkshape(solution, forbidden_pieces)
    Ty_len = len(target)
    Tx_len = len(target[0])
    Sy_len = len(solution)
    Sx_len = len(solution[0])

    fig, (ax1, ax2) = plt.subplots(1, 2)  # Create figure and axes
    im = Image.new('RGB', (Tx_len, Ty_len), (255, 255, 255))  # white background-image
    dr = ImageDraw.Draw(im)
    ax1.imshow(im)  # Display the background-image
    ax2.imshow(im)

    # -------------------- Target Display ----------------------
    for y in range(Ty_len):
        row = target[y]
        for x in range(Tx_len):
            if row[x] == 1:
                ax1.add_patch(patches.Rectangle((x, y), 0.88, 0.88, color='b'))  # draw a block
    ax1.set_title('The Display of Task')
    ax1.set_xlim([-1, Tx_len + 1])
    ax1.set_ylim([-1, Ty_len + 1])
    ax1.invert_yaxis()

    # --------------- Solution Display ----------------------
    def get_color(num):  # generate a random color
        np.random.seed(num)
        c = list(np.random.rand(3))
        c.append(1.0)
        return tuple(c)

    wrong_label_count = {}
    for y in range(Sy_len):
        row = solution[y]
        for x in range(Sx_len):
            shape, num = row[x]
            if shape != 0:
                ax2.add_patch(patches.Rectangle((x, y), 0.88, 0.88, color=get_color(num)))  # draw a block
                if num in wrong_list:
                    if wrong_label_count.setdefault(num, 0) == 0:
                        ax2.text(x, y + 0.8, '{}'.format(num))  # add label to blocks that have wrong shapes
                        wrong_label_count[num] += 1

    ax2.set_title('The Display of Solution')
    ax2.set_xlim([-1, Sx_len + 1])
    ax2.set_ylim([-1, Sy_len + 1])
    ax2.invert_yaxis()
    plt.show()

def visual_perfect(perfect, solution, forbidden_pieces):
    """
    Displays the perfect_solution vs the solution
    :param perfect: perfect solution
    :param solution: student's solution
    :param forbidden_pieces: set of forbidden shapeIDs 
    """
    wrong_list = checkshape(solution, forbidden_pieces)
    Ty_len = len(perfect)
    Tx_len = len(perfect[0])
    Sy_len = len(solution)
    Sx_len = len(solution[0])

    fig, (ax1, ax2) = plt.subplots(1, 2)  # Create figure and axes
    im = Image.new('RGB', (Tx_len, Ty_len), (255, 255, 255))  # white background-image
    dr = ImageDraw.Draw(im)
    ax1.imshow(im)  # Display the background-image
    ax2.imshow(im)

    def get_color(num):  # generate a random color
        np.random.seed(num)
        c = list(np.random.rand(3))
        c.append(1.0)
        return tuple(c)
    # -------------------- Perfect solution Display ----------------------
    for y in range(Ty_len):
        row = perfect[y]
        for x in range(Tx_len):
            shape, num = row[x]
            if shape != 0:
                ax1.add_patch(patches.Rectangle((x, y), 0.88, 0.88, color=get_color(num)))  # draw a block

    ax1.set_title('The Display of Perfect Solution')
    ax1.set_xlim([-1, Tx_len + 1])
    ax1.set_ylim([-1, Ty_len + 1])
    ax1.invert_yaxis()

    # --------------- Solution Display ----------------------
    wrong_label_count = {}
    for y in range(Sy_len):
        row = solution[y]
        for x in range(Sx_len):
            shape, num = row[x]
            if shape != 0:
                ax2.add_patch(patches.Rectangle((x, y), 0.88, 0.88, color=get_color(num)))  # draw a block
                if num in wrong_list:
                    if wrong_label_count.setdefault(num, 0) == 0:
                        ax2.text(x, y + 0.8, '{}'.format(num))  # add label to blocks that have wrong shapes
                        wrong_label_count[num] += 1

    ax2.set_title('The Display of Solution')
    ax2.set_xlim([-1, Sx_len + 1])
    ax2.set_ylim([-1, Sy_len + 1])
    ax2.invert_yaxis()
    plt.show()





"""
 ------------------------------- AUXILIARY FUNCTIONS ------------------------------- 
 The functions below are used by the main functions above, and you shouldn't need
 to call them directly from your code.
"""


def boundary_check(target, solution):
    """
    Counts the missing and excess blocks
    :param target: target shape
    :param solution: student's solution
    :return: missing: number of missing blocks
    :return: excess: number of excess blocks
    """

    missing = 0
    excess = 0

    height = len(target)
    width = len(target[0])

    if len(solution) != height:
        print("ERROR: The target and the solution are not the same size (target's height = {}, solution's height = {})."
              .format(height, len(solution)))
        return None, None

    for r in range(0, height):

        if len(target[r]) != width or len(solution[r]) != width:
            print("ERROR in row {}: The target and the solution are not the same size (target's width = {}, solution's "
                  "width = {}).".format(r, len(target[r]), len(solution[r])))
            return None, None

        for c in range(0, width):

            if target[r][c] == 0:
                if solution[r][c] != (0, 0):
                    excess += 1
            elif target[r][c] == 1:
                if solution[r][c] == (0, 0):
                    missing += 1
            else:
                print("ERROR in coordinates [x={}, y={}]: target block is {}, when it should be either 0 or 1"
                      .format(c, r, target[r][c]))
                return None, None

    return missing, excess


def checkposition(positions, shapeid, forbidden_pieces):
    """
    Check if positions of a piece corresponds with a specific shape
    :param positions: positions of blocks of a piece
    :param shapeid: the specified shape for this piece
    :param forbidden_pieces: set of forbidden shapeIDs
    :return: whether or not the positions are correct
    """
    # the relative position of the last three node to the first node
    goldenpositions = {
        1: np.array([[1, 0], [0, 1], [1, 1]]),
        2: np.array([[0, 1], [0, 2], [0, 3]]),
        3: np.array([[1, 0], [2, 0], [3, 0]]),
        4: np.array([[0, 1], [0, 2], [1, 2]]),
        5: np.array([[-2, 1], [-1, 1], [0, 1]]),
        6: np.array([[1, 0], [1, 1], [1, 2]]),
        7: np.array([[1, 0], [2, 0], [0, 1]]),
        8: np.array([[0, 1], [-1, 2], [0, 2]]),
        9: np.array([[1, 0], [2, 0], [2, 1]]),
        10: np.array([[1, 0], [0, 1], [0, 2]]),
        11: np.array([[0, 1], [1, 1], [2, 1]]),
        12: np.array([[0, 1], [1, 1], [0, 2]]),
        13: np.array([[-1, 1], [0, 1], [1, 1]]),
        14: np.array([[-1, 1], [0, 1], [0, 2]]),
        15: np.array([[1, 0], [2, 0], [1, 1]]),
        16: np.array([[1, 0], [-1, 1], [0, 1]]),
        17: np.array([[0, 1], [1, 1], [1, 2]]),
        18: np.array([[1, 0], [1, 1], [2, 1]]),
        19: np.array([[-1, 1], [0, 1], [-1, 2]])
    }

    matchM = (np.array(positions[1:])-np.array(positions[0]) == goldenpositions[shapeid])
    forbidden = False
    if not np.all(matchM):
        for f_pieces in forbidden_pieces:
            if np.all(np.array(positions[1:])-np.array(positions[0]) == goldenpositions[f_pieces]):
                print("ERROR, forbidden piece (shapeID {}) detected in position {}." .format(f_pieces, positions)) 
                forbidden = True
 
    return np.all(matchM), forbidden


def checkshape(solution, forbidden_pieces):
    """
    Check if the pieces have the correct shape
    :param solution: matrix containing the information of pieces, (shapeid, pieceid)
    :param forbidden_pieces: set of forbidden shapeIDs 
    :return:  id of pieces whose positions don't correspond with its shape
    """
    error_pieces = []
    Pieces = {}  # dictionary of pieces

    # extract all pieces from Matrix, and save their shapes and positions into Pieces
    for y, row in enumerate(solution):
        for x, point in enumerate(row):
            shapeid = point[0]
            pieceid = point[1]
            if 0 in [pieceid, shapeid]:
                if pieceid != 0:
                    print("ERROR in coordinates [x={}, y={}]: shapeID is 0, but shapeID should be greater than 0.".format(
                        x, y))
                    return None
                elif shapeid != 0:
                    print("ERROR in coordinates [x={}, y={}]: pieceID is 0, but pieceID should be greater than 0.".format(
                        x, y))
                    return None
                continue
            elif shapeid in forbidden_pieces:
                print("ERROR in pieces, there is a forbidden piece in the solution (shapeID = {}, pieceID = {}).".format(shapeid, pieceid))
                return None
            elif pieceid in Pieces:
                shapeid2 = Pieces[pieceid]['shape']
                if shapeid2 != shapeid:
                    print("ERROR in coordinates [x={}, y={}]: shapeID is {}, but it belongs to piece {}, whose shapeID "
                          "is {}.".format(x, y, shapeid, pieceid, shapeid2))
                    return None
                Pieces[pieceid]['node'].append((x, y))
            else:
                Pieces[pieceid] = {}
                Pieces[pieceid]['shape'] = shapeid
                Pieces[pieceid]['node'] = [(x, y)]

    # for each piece sort poisitions (left-right,up-down), and check if the position is correct
    for pid, piece in Pieces.items():
        piece['node'].sort(key=operator.itemgetter(1, 0))
        if len(piece['node']) != 4:
            print("ERROR: Piece {} has {} blocks (it should have 4).".format(pid, len(piece['node'])))
            return None
        no_error_pieces, forbidden_detected = checkposition(piece['node'], piece['shape'], forbidden_pieces)
        if no_error_pieces:
            continue
        else:
            if forbidden_detected:
                return None
            else:
                error_pieces.append(pid)

    return error_pieces

def check_if_piece_is_valid(piece, target):
    """
    Utility function called by generate_target
    :param piece: tentative piece
    :param target: target shape
    :return whether the piece is valid or not
    """
    valid = True
    height = len(target)
    width = len(target[0])
    for [r, c] in piece:
        if r < 0 or r >= height or c < 0 or c >= width:
            valid = False
            break
        elif target[r][c] == 1:
            valid = False
            break
    return valid


def generate_shape(shape_id):
    """
    Utility function called by generate_target
    """
    shape = None
    if shape_id == 1:
        shape = [[0, 0], [0, 1], [1, 0], [1, 1]]
    elif shape_id == 2:
        shape = [[0, 0], [1, 0], [2, 0], [3, 0]]
    elif shape_id == 3:
        shape = [[0, 0], [0, 1], [0, 2], [0, 3]]
    elif shape_id == 4:
        shape = [[0, 0], [1, 0], [2, 0], [2, 1]]
    elif shape_id == 5:
        shape = [[0, 0], [1, -2], [1, -1], [1, 0]]
    elif shape_id == 6:
        shape = [[0, 0], [0, 1], [1, 1], [2, 1]]
    elif shape_id == 7:
        shape = [[0, 0], [0, 1], [0, 2], [1, 0]]
    elif shape_id == 8:
        shape = [[0, 0], [1, 0], [2, -1], [2, 0]]
    elif shape_id == 9:
        shape = [[0, 0], [0, 1], [0, 2], [1, 2]]
    elif shape_id == 10:
        shape = [[0, 0], [0, 1], [1, 0], [2, 0]]
    elif shape_id == 11:
        shape = [[0, 0], [1, 0], [1, 1], [1, 2]]
    elif shape_id == 12:
        shape = [[0, 0], [1, 0], [1, 1], [2, 0]]
    elif shape_id == 13:
        shape = [[0, 0], [1, -1], [1, 0], [1, 1]]
    elif shape_id == 14:
        shape = [[0, 0], [1, -1], [1, 0], [2, 0]]
    elif shape_id == 15:
        shape = [[0, 0], [0, 1], [0, 2], [1, 1]]
    elif shape_id == 16:
        shape = [[0, 0], [0, 1], [1, -1], [1, 0]]
    elif shape_id == 17:
        shape = [[0, 0], [1, 0], [1, 1], [2, 1]]
    elif shape_id == 18:
        shape = [[0, 0], [0, 1], [1, 1], [1, 2]]
    elif shape_id == 19:
        shape = [[0, 0], [1, -1], [1, 0], [2, -1]]
    return shape
