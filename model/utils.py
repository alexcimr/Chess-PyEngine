def is_on_board(row, col):
    """Sprawdza, czy współrzędne istnieją na szachownicy"""
    return 0 <= row < 8 and 0 <= col < 8