# ####################################################
# DE2-COM2 Computing 2
# Individual project

# Title: PERFORMANCE TEST
# Authors: Liuqing Chen, Feng Shi, Isaac Engel, and
#          Nicolas Rojas
# ####################################################

from main import Tetris
import utils
import timeit
from copy import deepcopy # copy 'target' to avoid modifying it

the_forbidden_pieces = {1,2,3} #Forbidden shapeIDs

# Example target shape, limit_tetris, and perfect_solution
target = [
            [0, 0, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 0]
         ]
         
perfect_solution = [
                    [(0, 0),  (0, 0),  (8, 1),  (0, 0),   (0, 0),  (0, 0)],
                    [(0, 0),  (0, 0),  (8, 1),  (0, 0),   (13, 2), (0, 0)],
                    [(0, 0),  (8, 1),  (8, 1),  (13, 2),  (13, 2), (13, 2)],
                    [(0, 0),  (13, 3), (18, 4), (18, 4),  (0, 0),  (0, 0)],
                    [(13, 3), (13, 3), (13, 3), (18, 4),  (18, 4), (0, 0)]
                   ]

# NOTE: This example is used for the mock solution from 'main.py' only.

# Uncomment the following line to generate a random target shape
target, perfect_solution = utils.generate_target(width=40, height=40, density=0.8, forbidden_pieces=the_forbidden_pieces) # NOTE: it is recommended to keep density below 0.8

solution = Tetris(deepcopy(target))
valid, missing, excess, error_pieces = utils.check_solution(target, solution, the_forbidden_pieces)  # checks if the solution is valid

if not valid or len(error_pieces)!=0:
    if len(error_pieces) != 0:
        print('WARNING: {} pieces have a wrong shapeID. They are labelled in image of the solution, and their PieceID are: {}.'
                  .format(len(error_pieces), error_pieces))
        print("Displaying solution...")
        utils.visual_perfect(perfect_solution, solution, the_forbidden_pieces)
    print("WARNING: The solution is not valid, no score will be given!")

else:  # if the solution is valid, test time performance and accuracy

    # TIME PERFORMANCE
    # There will be three different 'target' with increasing complexity in real test.

    time_set = timeit.timeit('Tetris({})'.format(target), 'from main import Tetris', number=1)
    
    if time_set > 600:

        print("WARNING: Time is over 10 minutes! The solution is not valid")

    else:

        print("Time performance")
        print("----------------")
        print("The running time was {:.5f} seconds.\n".format(time_set))

        # ACCURACY

        print("Accuracy")
        print("--------")

        print('All pieces are labelled with correct shapeID and pieceID.')
        print('No forbidden pieces are used.')
        
        total_blocks = sum([sum(row) for row in target])
        total_blocks_solution = total_blocks - missing + excess

        print("The number of blocks in the TARGET is {:.0f}.".format(total_blocks))
        print("The number of blocks in the SOLUTION is {:.0f}.".format(total_blocks_solution))
        print("There are {} MISSING blocks ({:.4f}%) and {} EXCESS blocks ({:.4f}%).\n".format
              (missing, 100 * missing / total_blocks, excess, 100 * excess / total_blocks))

        # VISUALISATION
        # NOTE: for large sizes (e.g., 100x100), visualisation will take several seconds and might not be that helpful.
        # Feel free to comment out the following lines if you don't need the visual feedback.

        print("Displaying solution...")
        utils.visualisation(target, solution, the_forbidden_pieces)
        utils.visual_perfect(perfect_solution, solution, the_forbidden_pieces)