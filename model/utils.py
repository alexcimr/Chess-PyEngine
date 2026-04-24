def is_on_board(row, col):
    """
    Checks if the given coordinates are within the board boundaries (8x8 grid).
    """
    return 0 <= row < 8 and 0 <= col < 8