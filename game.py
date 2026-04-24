import pygame
import time
from model.enums import PieceType, Color, GameStatus
from model.board import Board
from model.bot import Bot

# --- Layout ---
BOARD_SIZE, SIDE_PANEL, MARGIN = 700, 250, 50
WINDOW_WIDTH  = BOARD_SIZE + SIDE_PANEL + (MARGIN * 2)
WINDOW_HEIGHT = BOARD_SIZE + (MARGIN * 2)
TILE_SIZE     = BOARD_SIZE // 8
PANEL_X       = BOARD_SIZE + MARGIN + 20
PANEL_WIDTH   = SIDE_PANEL - 20

# --- Colors ---
COLOR_LIGHT    = (240, 217, 181)
COLOR_DARK     = (181, 136, 99)
COLOR_BG       = (40, 40, 40)
COLOR_TEXT     = (255, 255, 255)
COLOR_SELECTED = (246, 229, 141)
COLOR_MOVE     = (90, 90, 90)

# --- UI Colors ---
COLOR_GREEN    = (103, 129, 97)  # Twój kolor z przycisku NEW GAME
COLOR_RED      = (180, 120, 120) # Kolor dla tury/wygranej Bota
COLOR_YELLOW   = (180, 150, 70)  # Kolor dla remisu
COLOR_BLUE     = (70, 100, 140)  # Kolor dla poziomu DEPTH

BOT_DEPTH = 5

PIECES = {
    (PieceType.KING,   Color.WHITE): "♔", (PieceType.QUEEN,  Color.WHITE): "♕",
    (PieceType.ROOK,   Color.WHITE): "♖", (PieceType.BISHOP, Color.WHITE): "♗",
    (PieceType.KNIGHT, Color.WHITE): "♘", (PieceType.PAWN,   Color.WHITE): "♙",
    (PieceType.KING,   Color.BLACK): "♚", (PieceType.QUEEN,  Color.BLACK): "♛",
    (PieceType.ROOK,   Color.BLACK): "♜", (PieceType.BISHOP, Color.BLACK): "♝",
    (PieceType.KNIGHT, Color.BLACK): "♞", (PieceType.PAWN,   Color.BLACK): "♟",
}


def draw_board(screen: pygame.Surface) -> None:
    """Draws the chessboard squares."""
    for row in range(8):
        for col in range(8):
            color = COLOR_LIGHT if (row + col) % 2 == 0 else COLOR_DARK
            pygame.draw.rect(screen, color,
                             (MARGIN + col * TILE_SIZE, MARGIN + row * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def draw_selected(screen: pygame.Surface, selected_sq: tuple | None) -> None:
    """Highlights the currently selected square."""
    if selected_sq is None:
        return
    r, c = selected_sq
    x = MARGIN + (7 - c) * TILE_SIZE
    y = MARGIN + (7 - r) * TILE_SIZE
    pygame.draw.rect(screen, COLOR_SELECTED, (x, y, TILE_SIZE, TILE_SIZE), 5)


def draw_coordinates(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Draws rank numbers and file letters around the board."""
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    numbers = ['8', '7', '6', '5', '4', '3', '2', '1']
    for i in range(8):
        char_surf = font.render(letters[i], True, COLOR_TEXT)
        x = MARGIN + i * TILE_SIZE + (TILE_SIZE // 2) - (char_surf.get_width() // 2)
        screen.blit(char_surf, (x, MARGIN + BOARD_SIZE + 10))

        num_surf = font.render(numbers[i], True, COLOR_TEXT)
        y = MARGIN + i * TILE_SIZE + (TILE_SIZE // 2) - (num_surf.get_height() // 2)
        screen.blit(num_surf, (MARGIN - 30, y))


def draw_menu(
    screen: pygame.Surface,
    font: pygame.font.Font,
    button_rect: pygame.Rect,
    msg: str,
    bot_time: float,
    turn: Color,
    active: bool,
) -> None:
    """Draws the side panel with depth, turn indicator/game over status, bot time and buttons."""
    pygame.draw.rect(screen, (60, 60, 60), (PANEL_X, MARGIN, PANEL_WIDTH, BOARD_SIZE), border_radius=10)

    # Depth label
    depth_rect = pygame.Rect(PANEL_X + (PANEL_WIDTH - 200) // 2, MARGIN + 20, 200, 40)
    pygame.draw.rect(screen, COLOR_BLUE, depth_rect, border_radius=20)
    d = font.render(f"DEPTH: {BOT_DEPTH}", True, COLOR_TEXT)
    screen.blit(d, (depth_rect.centerx - d.get_width() // 2, depth_rect.centery - d.get_height() // 2))

    # Turn indicator OR Game Over message
    if active:
        turn_text = "Your Turn" if turn == Color.WHITE else "Bot's Turn"
        turn_color = COLOR_GREEN if turn == Color.WHITE else COLOR_RED
    else:
        turn_text = msg
        if "You Win" in msg:
            turn_color = COLOR_GREEN
        elif "Bot Wins" in msg:
            turn_color = COLOR_RED
        else:
            turn_color = COLOR_YELLOW

    turn_rect = pygame.Rect(PANEL_X + (PANEL_WIDTH - 200) // 2, MARGIN + 70, 200, 40)
    pygame.draw.rect(screen, turn_color, turn_rect, border_radius=20)
    t = font.render(turn_text, True, COLOR_TEXT)
    screen.blit(t, (turn_rect.centerx - t.get_width() // 2, turn_rect.centery - t.get_height() // 2))

    # Bot thinking time
    if bot_time > 0:
        bt = font.render(f"Bot thought: {bot_time:.2f}s", True, (200, 200, 200))
        screen.blit(bt, (PANEL_X + PANEL_WIDTH // 2 - bt.get_width() // 2, MARGIN + 120))

    # New game button
    pygame.draw.rect(screen, COLOR_GREEN, button_rect, border_radius=20)
    ng = font.render("NEW GAME", True, COLOR_TEXT)
    screen.blit(ng, (button_rect.centerx - ng.get_width() // 2, button_rect.centery - ng.get_height() // 2))


def draw_pieces(screen: pygame.Surface, board: Board, font: pygame.font.Font) -> None:
    """Draws all pieces on the board using Unicode chess glyphs."""
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p:
                glyph = PIECES[(p.type, p.color)]
                color = (255, 255, 255) if p.color == Color.WHITE else (0, 0, 0)
                surf = font.render(glyph, True, color)
                cx = MARGIN + (7 - c) * TILE_SIZE + (TILE_SIZE // 2)
                cy = MARGIN + (7 - r) * TILE_SIZE + (TILE_SIZE // 2)
                screen.blit(surf, surf.get_rect(center=(cx, cy)))


def draw_highlights(screen: pygame.Surface, moves: list) -> None:
    """Draws move hint dots on legal destination squares."""
    for (r, c), _ in moves:
        cx = MARGIN + (7 - c) * TILE_SIZE + TILE_SIZE // 2
        cy = MARGIN + (7 - r) * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, COLOR_MOVE, (cx, cy), 12)


def get_board_pos(pos: tuple) -> tuple | None:
    """Converts a screen (x, y) position to board (row, col) coordinates."""
    c_screen = (pos[0] - MARGIN) // TILE_SIZE
    r_screen = (pos[1] - MARGIN) // TILE_SIZE
    if 0 <= c_screen < 8 and 0 <= r_screen < 8:
        return (7 - r_screen, 7 - c_screen)
    return None


def new_game() -> tuple[Board, Bot]:
    """Creates a new board and bot instance."""
    board = Board()
    board.setup_start_position()
    bot = Bot(board)
    return board, bot


def get_endgame_message(status: GameStatus, checked_color: Color) -> str:
    """Returns a specific message indicating who won or if it's a draw."""
    if status == GameStatus.CHECKMATE:
        return "Bot Wins!" if checked_color == Color.WHITE else "You Win!"
    if status == GameStatus.STALEMATE:
        return "Draw!"
    return ""


def play_game() -> None:
    global BOT_DEPTH
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess")

    font   = pygame.font.SysFont("Arial", 20, bold=True)
    font_p = pygame.font.SysFont("segoeuisymbol", 70)

    btn = pygame.Rect(
        PANEL_X + (PANEL_WIDTH - 200) // 2,
        MARGIN + BOARD_SIZE - 75,
        200, 60
    )

    board, bot = new_game()
    clock = pygame.time.Clock()

    sel, moves, turn, active, msg, b_time = None, [], Color.WHITE, True, "", 0

    # Depth increases as material decreases
    flag32 = flag13 = flag6 = flag3 = True

    while True:
        # --- Bot's turn ---
        if active and turn == Color.BLACK:
            st = time.time()
            mats = board.material_on_board()

            if mats <= 32 and flag32:
                BOT_DEPTH += 1
                flag32 = False
            if mats <= 13 and flag13:
                BOT_DEPTH += 1
                flag13 = False
            if mats <= 6 and flag6:
                BOT_DEPTH += 1
                flag6 = False
            if mats <= 3 and flag3:
                BOT_DEPTH += 1
                flag3 = False

            m = bot.best_move(depth=BOT_DEPTH, maximazing_color=Color.BLACK)
            b_time = time.time() - st

            if m:
                board.make_move(*m)
                status = board.game_status(Color.WHITE)
                if status != GameStatus.NORMAL:
                    msg, active = get_endgame_message(status, Color.WHITE), False
                turn = Color.WHITE
            else:
                msg, active = "BOT HAS NO MOVES", False

        # --- Events ---
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(ev.pos):
                    board, bot = new_game()
                    sel, moves, turn, active, msg, b_time = None, [], Color.WHITE, True, "", 0
                    BOT_DEPTH = 5
                    flag32 = flag13 = flag6 = flag3 = True
                    continue

                if active and turn == Color.WHITE:
                    p = get_board_pos(ev.pos)
                    if p:
                        exec_m = next((m[1] for m in moves if m[0] == p), None)
                        if sel and exec_m:
                            board.make_move(sel, p, exec_m)
                            status = board.game_status(Color.BLACK)
                            if status != GameStatus.NORMAL:
                                msg, active = get_endgame_message(status, Color.BLACK), False
                            sel, moves, turn = None, [], Color.BLACK
                        else:
                            pc = board.grid[p[0]][p[1]]
                            if pc and pc.color == Color.WHITE:
                                sel, moves = p, board.get_legal_moves(p[0], p[1])
                            else:
                                sel, moves = None, []

        # --- Draw ---
        screen.fill(COLOR_BG)
        draw_board(screen)
        draw_selected(screen, sel)
        draw_highlights(screen, moves)
        draw_pieces(screen, board, font_p)
        draw_coordinates(screen, font)
        draw_menu(screen, font, btn, msg, b_time, turn, active)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    play_game()