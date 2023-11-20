import chess
import chess.pgn
import pandas as pd


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


def get_attack_count_by_color(chess_board: chess.Board, color: str):
    """
    This function returns the amount of times each square is attacked by pieces of the given color.
    :param chess_board: board object
    :param color: "white" or "black"
    :return: dict object with squares as indices. Squares are given as integers in range(64).
    """
    occupied_squares = get_occupied_squares_by_color(chess_board, color)

    attack_count = {
        square: 0 for square in chess.SQUARES
    }

    for square in occupied_squares:
        attacked_squares = chess_board.attacks(square).tolist()

        for square_ in chess.SQUARES:
            if attacked_squares[square_]:
                attack_count[square_] += 1

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
