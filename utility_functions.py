import chess
import chess.pgn
import numpy
import pandas as pd
import numpy as np
from math import exp


def get_occupied_squares_by_color(board: chess.Board,
                                  color: str):
    """
    This function returns the list of squares occupied by pieces of the given color on the given board.
    :param board: chess.Board object.
    :param color: strings "white" or "black"
    :return: list of squares written with
    """
    if str.lower(color) == "white":
        color = chess.WHITE
    elif str.lower(color) == "black":
        color = chess.BLACK
    else:
        return ValueError("parameters of the functions should be white or black (case insensitive)")

    squares = []
    for square in chess.SQUARES:
        if board.piece_at(square) is not None and board.piece_at(square).color == color:
            squares.append(square)

    return squares


def square_numb_to_2d_coords(square_numb:int):
    """
    This method translates the chess package's square numbering system to a 2D index
    :param square_numb: square number as described in the package
    :return: [x, y] where x and y are the indices on the array
    """
    return [
        square_numb // 8,
        square_numb % 8
    ]


def get_attack_count_by_color(chess_board: chess.Board, color: str):
    """
    This function returns the amount of times each square is attacked by pieces of the given color.
    :param chess_board: board object
    :param color: "white" or "black"
    :return: 2D array of each square and how much it is attacked by the given color for that board state
    """

    # create zeros 8x8 array
    attack_count = np.zeros(shape=(8, 8), dtype=numpy.int8)

    # get occupied squares
    occupied_squares = get_occupied_squares_by_color(chess_board, color)

    for square in occupied_squares:
        # get squares that are attacked
        attacked_squares = chess_board.attacks(square).tolist()

        # increment attack count in 2d matrix
        for square_ in chess.SQUARES:
            if attacked_squares[square_]:
                [x, y] = square_numb_to_2d_coords(square_)
                attack_count[x][y] += 1

    return attack_count


def get_game_as_attack_df(game: chess.pgn.Game):
    """
    This function returns a dataframe which shows for each move, the squares attacked by black pieces and by white
    pieces and how many times.
    :param game: game as read by file
    :return: dataframe with move number as indices, and columns ["white", "black"]
    """
    game_board = game.board()

    game_as_attacks_df = pd.DataFrame(columns=["white", "black"])

    game_as_attacks_df.loc[0] = [
        get_attack_count_by_color(game_board, "white"),
        get_attack_count_by_color(game_board, "black")
    ]

    for i, move in enumerate(game.mainline_moves()):
        game_board.push(move)
        game_as_attacks_df.loc[i] = [
            get_attack_count_by_color(game_board, "white"),
            get_attack_count_by_color(game_board, "black")
        ]

    return game_as_attacks_df


def coords_to_square_numb(x: int, y: int):
    """
    This method translates 2d array indexes to the chess package's square numbering system
    :param x: array column index
    :param y: array row index
    :return: integer value [0, 64] representing a square on the chess board
    """
    return x * 8 + y


def get_attack_numb_from_2d_coords(X, Y, attack_dict: dict):
    """
    Given meshgrids X and Y, this method creates the values for Z by looking up in the attack dicti
    :param X: meshgrid for X  2D array
    :param Y: meshgrid for Y  2D array
    :param attack_dict: dict that contains
    :return:
    """

    Z = coords_to_square_numb(X, Y)

    # creates the attack meshgrid by changing values in Z
    for i in range(len(Z)):
        for j in range(len(Z[0])):
            Z[i][j] = attack_dict[Z[i][j]]

    return Z


def gaussian_3d(x, y,
                height_of_hill, spread,
                peak_position_x, peak_position_y):

    var_1 = ((x-peak_position_x)**2)/(2 * spread ** 2)
    var_2 = ((y-peak_position_y)**2)/(2 * spread ** 2)

    return height_of_hill * exp(-(var_1 + var_2))


def create_XYZ(attack_matrix, datapoints_along_square: int):
    """
    Given the attack count matrix, this method outputs a smoothed out gaussian hill folllowing the values of the matrix.
    :param attack_matrix: 2D matrix with count for each square
    :param datapoints_along_square: to smooth out surface of the hill on one square, we create more datapoints to describe a square. this parameter controls how many datapoints are used for one square. the value is the number along one side of the square.
    :return: (X, Y, Z) where those are the matrices needed for the 3D plot.
    """

    dal = datapoints_along_square
    datapoints_along_board = dal * 8

    X = np.arange(0, datapoints_along_board)
    Y = np.arange(0, datapoints_along_board)

    X, Y = np.meshgrid(X, Y)

    Z = np.zeros(shape=(datapoints_along_board, datapoints_along_board))

    for i in range(8):
        for j in range(8):

            attack_count = attack_matrix[i][j]

            # defining peak coordinates
            peak_x = (i * dal) + dal / 2
            peak_y = (j * dal) + dal / 2

            # define spreads
            spread = dal / 2

            # define values
            for k in range(i * dal, (i + 1) * dal):
                for l in range(j * dal, (j + 1) * dal):
                    Z[k][l] = gaussian_3d(
                        x=k, y=l,
                        height_of_hill=attack_count,
                        spread=spread,
                        peak_position_x=peak_x,
                        peak_position_y=peak_y
                    )

    return X, Y, Z
