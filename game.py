import pygame
import time
from model.enums import PieceType, Color, GameStatus
from model.board import Board
from model.bot import Bot

BOARD_SIZE, SIDE_PANEL, MARGIN = 700, 250, 50
WINDOW_WIDTH = BOARD_SIZE + SIDE_PANEL + (MARGIN * 2)
WINDOW_HEIGHT = BOARD_SIZE + (MARGIN * 2)
TILE_SIZE = BOARD_SIZE // 8
PANEL_X = BOARD_SIZE + MARGIN + 20
PANEL_WIDTH = SIDE_PANEL - 20

COLOR_LIGHT, COLOR_DARK = (240, 217, 181), (181, 136, 99)
COLOR_BG, COLOR_TEXT = (40, 40, 40), (255, 255, 255)
COLOR_SELECTED = (246, 229, 141)
COLOR_MOVE = (90, 90, 90)
BOT_DEPTH = 5

PIECES = {
    (PieceType.KING, Color.WHITE): "♔", (PieceType.QUEEN, Color.WHITE): "♕",
    (PieceType.ROOK, Color.WHITE): "♖", (PieceType.BISHOP, Color.WHITE): "♗",
    (PieceType.KNIGHT, Color.WHITE): "♘", (PieceType.PAWN, Color.WHITE): "♙",
    (PieceType.KING, Color.BLACK): "♚", (PieceType.QUEEN, Color.BLACK): "♛",
    (PieceType.ROOK, Color.BLACK): "♜", (PieceType.BISHOP, Color.BLACK): "♝",
    (PieceType.KNIGHT, Color.BLACK): "♞", (PieceType.PAWN, Color.BLACK): "♟",
}

def draw_board(screen):
    """Rysuje Szachownice"""
    for row in range(8):
        for col in range(8):
            color = COLOR_LIGHT if (row + col) % 2 == 0 else COLOR_DARK
            pygame.draw.rect(screen, color, (MARGIN + col * TILE_SIZE, MARGIN + row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_selected(screen, selected_sq):
    """Podswietla wybrane pole."""
    if selected_sq is None:
        return

    r, c = selected_sq
    x = MARGIN + (7 - c) * TILE_SIZE
    y = MARGIN + (7 - r) * TILE_SIZE
    pygame.draw.rect(screen, COLOR_SELECTED, (x, y, TILE_SIZE, TILE_SIZE), 5)

def draw_coordinates(screen, font):
    """Rysuje koordynaty."""
    # Litery A-H (wyświetlane od lewej do prawej)
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    # Cyfry 8-1 (od góry do dołu)
    numbers = ['8', '7', '6', '5', '4', '3', '2', '1']
    for i in range(8):
        char_surf = font.render(letters[i], True, COLOR_TEXT)
        x = MARGIN + i * TILE_SIZE + (TILE_SIZE // 2) - (char_surf.get_width() // 2)
        screen.blit(char_surf, (x, MARGIN + BOARD_SIZE + 10))
        num_surf = font.render(numbers[i], True, COLOR_TEXT)
        y = MARGIN + i * TILE_SIZE + (TILE_SIZE // 2) - (num_surf.get_height() // 2)
        screen.blit(num_surf, (MARGIN - 30, y))

def draw_menu(screen, font, button_rect, msg, bot_time):
    px = PANEL_X
    pygame.draw.rect(screen, (60, 60, 60), (px, MARGIN, PANEL_WIDTH, BOARD_SIZE), border_radius=10)

    depth_rect = pygame.Rect(px + (PANEL_WIDTH - 200) // 2, MARGIN + 20, 200, 40)
    pygame.draw.rect(screen, (70, 100, 140), depth_rect, border_radius=20)
    d = font.render(f"GŁĘBOKOŚĆ: {BOT_DEPTH}", True, COLOR_TEXT)
    screen.blit(d, (depth_rect.centerx - d.get_width() // 2, depth_rect.centery - d.get_height() // 2))

    if bot_time > 0:
        t = font.render(f"BOT MYŚLAŁ: {bot_time:.2f}s", True, (200, 200, 200))
        screen.blit(t, (px + PANEL_WIDTH // 2 - t.get_width() // 2, MARGIN + 80))

    if msg:
        msg_rect = pygame.Rect(px + (PANEL_WIDTH - 200) // 2, MARGIN + 120, 200, 40)
        pygame.draw.rect(screen, (140, 60, 60), msg_rect, border_radius=20)
        s = font.render(msg, True, COLOR_TEXT)
        screen.blit(s, (msg_rect.centerx - s.get_width() // 2, msg_rect.centery - s.get_height() // 2))

    pygame.draw.rect(screen, (103, 129, 97), button_rect, border_radius=20)
    bt = font.render("NOWA GRA", True, COLOR_TEXT)
    screen.blit(bt, (button_rect.centerx - bt.get_width() // 2, button_rect.centery - bt.get_height() // 2))

def draw_pieces(screen, board, font):
    """Rysuje figruy na szachownicy"""
    for r in range(8):
        for c in range(8):
            p = board.grid[r][c]
            if p:
                glyph = PIECES[(p.type, p.color)]
                color = (255, 255, 255) if p.color == Color.WHITE else (0, 0, 0)
                surf = font.render(glyph, True, color)
                # NAPRAWA: 7-c zamienia strony, żeby Król był po prawej (e1)
                cx = MARGIN + (7 - c) * TILE_SIZE + (TILE_SIZE // 2)
                cy = MARGIN + (7 - r) * TILE_SIZE + (TILE_SIZE // 2)
                screen.blit(surf, surf.get_rect(center=(cx, cy)))

def draw_highlights(screen, moves):
    """Rysuje kropki podpowiedzi."""
    for (r, c), _ in moves:
        # NAPRAWA: Tu też 7-c, żeby kropki trafiały w figury
        cx = MARGIN + (7 - c) * TILE_SIZE + TILE_SIZE // 2
        cy = MARGIN + (7 - r) * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, COLOR_MOVE, (cx, cy), 12)

def get_board_pos(pos):
    """Zamienia (x, y) myszki na (row, col) szachownicy."""
    c_screen = (pos[0] - MARGIN) // TILE_SIZE
    r_screen = (pos[1] - MARGIN) // TILE_SIZE
    if 0 <= c_screen < 8 and 0 <= r_screen < 8:
        # NAPRAWA: 7-c_screen, żeby kliknięcie pasowało do wyświetlania
        return (7 - r_screen, 7 - c_screen)
    return None

def new_game():
    """Tworzy nowa plansze i nowego bota."""
    board = Board()
    board.setup_start_position()
    bot = Bot(board)
    return board, bot

def status_text(status):
    if status == GameStatus.CHECKMATE:
        return "MAT"
    if status == GameStatus.STALEMATE:
        return "PAT"
    return "GRA TRWA"

def play_game():
    global BOT_DEPTH
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font, font_p = pygame.font.SysFont("Arial", 20, bold=True), pygame.font.SysFont("segoeuisymbol", 70)
    btn_width, btn_height = 200, 60
    btn = pygame.Rect(PANEL_X + (PANEL_WIDTH - btn_width) // 2, MARGIN + BOARD_SIZE - 75, btn_width, btn_height)
    board, bot = new_game()
    clock = pygame.time.Clock()
    sel, moves, turn, active, msg, b_time = None, [], Color.WHITE, True, "", 0

    flag32 = True
    flag20 = True
    flag6 = True
    flag3 = True
    while True:
        if active and turn == Color.BLACK:
            st = time.time()
            mats = board.material_on_board()
            if mats <= 32 and flag32:
                BOT_DEPTH += 1
                flag32 = False
            if mats <= 20 and flag20:
                BOT_DEPTH += 1
                flag20 = False
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
                    msg, active = "KONIEC: " + status_text(status), False
                turn = Color.WHITE
            else:
                msg, active = "BOT NIE MA RUCHU", False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); return
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(ev.pos):
                    board, bot = new_game()
                    sel, moves, turn, active, msg, b_time = None, [], Color.WHITE, True, "", 0

                    BOT_DEPTH = 5
                    flag32 = flag20 = flag6 = flag3 = True
                    continue

                if active and turn == Color.WHITE:
                    p = get_board_pos(ev.pos)
                    if p:
                        exec_m = next((m[1] for m in moves if m[0] == p), None)
                        if sel and exec_m:
                            board.make_move(sel, p, exec_m)
                            status = board.game_status(Color.BLACK)
                            if status != GameStatus.NORMAL:
                                msg, active = "KONIEC: " + status_text(status), False
                            sel, moves, turn = None, [], Color.BLACK
                        else:
                            pc = board.grid[p[0]][p[1]]
                            if pc and pc.color == Color.WHITE:
                                sel, moves = p, board.get_legal_moves(p[0], p[1])
                            else:
                                sel, moves = None, []

        screen.fill(COLOR_BG)
        draw_board(screen)
        draw_selected(screen, sel)
        draw_highlights(screen, moves)
        draw_pieces(screen, board, font_p)
        draw_coordinates(screen, font)
        draw_menu(screen, font, btn, msg, b_time)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    play_game()
