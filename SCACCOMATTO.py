import pygame
import os
import random

pygame.init()

# ---------------- DISPLAY & SETUP ----------------
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SCACCOMATTO")
clock = pygame.time.Clock()

BOARD_SIZE = 560
TILE = BOARD_SIZE // 8

OFFSET_X = (WIDTH - BOARD_SIZE) // 2
OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2

BORDER_THICKNESS = 12

PIECE_SIZE = int(TILE * 0.90)
PIECE_OFFSET = (TILE - PIECE_SIZE) // 2

MENU_GRID_OFFSET_X = 25
MENU_GRID_OFFSET_Y = 25

# ---------------- COLORS ----------------
BG_WHITE = (240, 240, 240)
BG_BLACK = (30, 30, 30)

LIGHT = (200, 200, 200)
DARK = (120, 120, 120)
BOARD_BORDER_COLOR = (70, 70, 70)  

SELECT_LIGHT = (190, 235, 255)   
SELECT_DARK = (110, 180, 220)     

MOVE_LIGHT = (170, 225, 255)     
MOVE_DARK = (90, 170, 210)      

CAPT_LIGHT = (255, 255, 170)     
CAPT_DARK = (195, 195, 80)       

KING_CAPT_LIGHT = (144, 238, 144) 
KING_CAPT_DARK = (60, 179, 113)   

# Colore speciale per l'Arrocco (Verde Chiaro)
CASTLE_LIGHT = (160, 255, 160)
CASTLE_DARK = (90, 200, 90)

# Colore speciale per lo Scacco (Rosso)
CHECK_RED_LIGHT = (255, 120, 120)
CHECK_RED_DARK = (220, 80, 80)

WHITE = (255, 255, 255)
YELLOW = (255, 235, 120)
MINECRAFT_ORANGE = (255, 180, 50)  
QUIT_RED = (180, 70, 70)           
GREEN_TEXT = (144, 238, 144)     
CREDITS_GRAY = (180, 180, 180)

# ---------------- FONT PERSONALIZZATO ----------------
FONT_PATH = os.path.join("assets", "pixel_font.ttf")

def get_font(size):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except:
        return pygame.font.SysFont("impact", size)

font_splash = get_font(28) 
font_small = get_font(30)
font = get_font(50)
font_big = get_font(75)
font_title = get_font(110)

# ---------------- CARICAMENTO ASSET PNG ----------------
PIECE_IMAGES = {}
pieces_names = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]

piece_names_map = {"p": "pawn", "r": "tower", "n": "knight", "b": "bishop", "q": "queen", "k": "king"}
color_names_map = {"w": "white", "b": "black"}

for name in pieces_names:
    color_str = color_names_map[name[0]]
    piece_str = piece_names_map[name[1]]
    filename = f"spr_{piece_str}_{color_str}.png"
    path = os.path.join("assets", filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        PIECE_IMAGES[name] = pygame.transform.scale(img, (PIECE_SIZE, PIECE_SIZE))
    except FileNotFoundError:
        pass

# ---------------- VARIABILI DI STATO GLOBALI ----------------
board = []
selected = None
valid_moves = []
turn = "w"
game_over = False
winner = ""
last_double_pawn = None

game_state = "MENU"
play_rect = None
quit_rect = None
rematch_rect = None
win_quit_rect = None

# Tracciamento movimento per l'Arrocco
has_moved = {
    "wk": False, "bk": False,
    "wr_l": False, "wr_r": False, 
    "br_l": False, "br_r": False
}

menu_bg_pieces = []
def generate_menu_background():
    global menu_bg_pieces
    menu_bg_pieces = []
    for _ in range(random.randint(12, 18)):
        rx = random.randint(-1, 8)
        ry = random.randint(-1, 8)
        r_piece = random.choice(pieces_names)
        if (rx, ry) not in [(p[0], p[1]) for p in menu_bg_pieces]:
            menu_bg_pieces.append((rx, ry, r_piece))

generate_menu_background()

# ---------------- RESET GAME ----------------
def reset_game():
    global board, selected, valid_moves, turn, game_over, winner, last_double_pawn, has_moved
    
    board = [
        ["br","bn","bb","bq","bk","bb","bn","br"],
        ["bp","bp","bp","bp","bp","bp","bp","bp"],
        ["","","","","","","",""],
        ["","","","","","","",""],
        ["","","","","","","",""],
        ["","","","","","","",""],
        ["wp","wp","wp","wp","wp","wp","wp","wp"],
        ["wr","wn","wb","wq","wk","wb","wn","wr"]
    ]
    
    selected = None
    valid_moves = []
    turn = "w"
    game_over = False
    winner = ""
    last_double_pawn = None
    
    has_moved = {
        "wk": False, "bk": False,
        "wr_l": False, "wr_r": False, 
        "br_l": False, "br_r": False
    }

reset_game()

# ---------------- MENU PRINCIPALE ----------------
def draw_main_menu():
    global play_rect, quit_rect
    
    tile_w = WIDTH // 8
    tile_h = HEIGHT // 8
    
    for y in range(-1, 9): 
        for x in range(-1, 9):
            color = LIGHT if (x+y)%2==0 else DARK
            pygame.draw.rect(screen, color, (x * tile_w + MENU_GRID_OFFSET_X, y * tile_h + MENU_GRID_OFFSET_Y, tile_w, tile_h))
            
    for rx, ry, r_piece in menu_bg_pieces:
        if r_piece in PIECE_IMAGES:
            px = rx * tile_w + MENU_GRID_OFFSET_X + (tile_w - PIECE_SIZE) // 2
            py = ry * tile_h + MENU_GRID_OFFSET_Y + (tile_h - PIECE_SIZE) // 2
            screen.blit(PIECE_IMAGES[r_piece], (px, py))
            
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))
    
    title_surf = font_title.render("SCACCOMATTO", True, YELLOW)
    title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 90))
    screen.blit(title_surf, title_rect)
    
    splash_text = "by Mc Quer Albs Studios"
    splash_surf = font_splash.render(splash_text, True, MINECRAFT_ORANGE)
    rotated_splash = pygame.transform.rotate(splash_surf, 15)
    splash_rect = rotated_splash.get_rect()
    splash_rect.left = title_rect.right - 80
    splash_rect.bottom = title_rect.top + 30
    screen.blit(rotated_splash, splash_rect)
    
    play_surf = font.render("- Play -", True, WHITE)
    play_rect = play_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    screen.blit(play_surf, play_rect)
    
    quit_surf = font.render("- Quit -", True, QUIT_RED)
    quit_rect = quit_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
    screen.blit(quit_surf, quit_rect)
    
    credits_surf = font_small.render("by Mc Quer Albs Studios", True, CREDITS_GRAY)
    credits_rect = credits_surf.get_rect(bottomleft=(30, HEIGHT - 30))
    screen.blit(credits_surf, credits_rect)

# ---------------- WIN SCREEN ----------------
def draw_win_screen(winner_text):
    global rematch_rect, win_quit_rect
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    band = pygame.Surface((WIDTH, 260), pygame.SRCALPHA)
    band.fill((0, 0, 0, 180))
    band_rect = band.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(band, band_rect.topleft)

    text_surf = font_big.render(winner_text + "!", True, GREEN_TEXT)
    text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    screen.blit(text_surf, text_rect)

    rematch_surf = font.render("- REMATCH -", True, WHITE)
    rematch_rect = rematch_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 15))
    screen.blit(rematch_surf, rematch_rect)
    
    win_quit_surf = font.render("- Quit -", True, QUIT_RED)
    win_quit_rect = win_quit_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 75))
    screen.blit(win_quit_surf, win_quit_rect)

# ---------------- LOGICA SCACCHI ----------------
def path_clear(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    cx, cy = x1 + step_x, y1 + step_y
    while (cx, cy) != (x2, y2):
        if board[cy][cx] != "": return False
        cx += step_x
        cy += step_y
    return True

def attacks_square(ex, ey, tx, ty, piece):
    """Verifica se un pezzo in (ex, ey) attacca la casella (tx, ty) ignorando regole speciali"""
    color = piece[0]
    kind = piece[1]
    dx, dy = tx - ex, ty - ey
    
    if kind == "p":
        direction = -1 if color == "w" else 1
        return abs(dx) == 1 and dy == direction
    if kind == "r": return (dx == 0 or dy == 0) and path_clear(ex, ey, tx, ty)
    if kind == "b": return (abs(dx) == abs(dy)) and path_clear(ex, ey, tx, ty)
    if kind == "q": return (dx == 0 or dy == 0 or abs(dx) == abs(dy)) and path_clear(ex, ey, tx, ty)
    if kind == "n": return (abs(dx), abs(dy)) in [(1,2), (2,1)]
    if kind == "k": return abs(dx) <= 1 and abs(dy) <= 1
    return False

def is_under_attack(tx, ty, color):
    """Restituisce True se (tx, ty) è attaccata da un pezzo nemico (diverso da 'color')"""
    for y in range(8):
        for x in range(8):
            p = board[y][x]
            if p != "" and p[0] != color:
                if attacks_square(x, y, tx, ty, p): return True
    return False

def get_check_path(color):
    """Trova il percorso rosso se il re di 'color' è sotto scacco."""
    # Trova il re
    kx, ky = -1, -1
    for y in range(8):
        for x in range(8):
            if board[y][x] == color + "k":
                kx, ky = x, y
                break
    if kx == -1: return [] # Re non trovato (strano)
    
    path = []
    for y in range(8):
        for x in range(8):
            p = board[y][x]
            if p != "" and p[0] != color:
                if attacks_square(x, y, kx, ky, p):
                    path.append((kx, ky))
                    path.append((x, y))
                    # Se è torre, alfiere o regina aggiunge le caselle intermedie
                    if p[1] in ['r', 'b', 'q']:
                        dx, dy = kx - x, ky - y
                        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
                        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
                        cx, cy = x + step_x, y + step_y
                        while (cx, cy) != (kx, ky):
                            path.append((cx, cy))
                            cx += step_x
                            cy += step_y
    return path

def valid_move(x1, y1, x2, y2):
    piece = board[y1][x1]
    if piece == "": return False
    color = piece[0]
    kind = piece[1]
    target = board[y2][x2]
    
    if target != "" and target[0] == color: return False
    dx, dy = x2 - x1, y2 - y1

    # Arrocco
    if kind == "k" and abs(dx) == 2 and dy == 0:
        row = 7 if color == "w" else 0
        if y1 != row or y2 != row: return False
        
        # Lato Destro (Corto)
        if dx == 2:
            rook_key = "wr_r" if color == "w" else "br_r"
            if not has_moved[color + "k"] and not has_moved.get(rook_key, False):
                if board[row][5] == "" and board[row][6] == "":
                    if not is_under_attack(4, row, color) and not is_under_attack(5, row, color) and not is_under_attack(6, row, color):
                        return True
        # Lato Sinistro (Lungo)
        elif dx == -2:
            rook_key = "wr_l" if color == "w" else "br_l"
            if not has_moved[color + "k"] and not has_moved.get(rook_key, False):
                if board[row][1] == "" and board[row][2] == "" and board[row][3] == "":
                    if not is_under_attack(4, row, color) and not is_under_attack(3, row, color) and not is_under_attack(2, row, color):
                        return True
        return False

    if kind == "p":
        direction = -1 if color == "w" else 1
        if dx == 0 and target == "":
            if dy == direction: return True
            if (y1 == 6 and color == "w") or (y1 == 1 and color == "b"):
                if dy == 2*direction and board[y1+direction][x1] == "": return True
        if abs(dx) == 1 and dy == direction and target != "": return True
        global last_double_pawn
        if abs(dx) == 1 and dy == direction and target == "":
            if last_double_pawn:
                lx, ly, lc = last_double_pawn
                if lc != color and lx == x2 and ly == y1: return True
                
    if kind == "r": return (dx == 0 or dy == 0) and path_clear(x1, y1, x2, y2)
    if kind == "b": return (abs(dx) == abs(dy)) and path_clear(x1, y1, x2, y2)
    if kind == "q": return (dx == 0 or dy == 0 or abs(dx) == abs(dy)) and path_clear(x1, y1, x2, y2)
    if kind == "n": return (abs(dx), abs(dy)) in [(1,2), (2,1)]
    if kind == "k": return abs(dx) <= 1 and abs(dy) <= 1
    
    return False

# ---------------- DISEGNO GIOCO ----------------
def draw_highlights():
    if selected:
        x, y = selected
        sel_color = SELECT_LIGHT if (x + y) % 2 == 0 else SELECT_DARK
        pygame.draw.rect(screen, sel_color, (OFFSET_X + x * TILE, OFFSET_Y + y * TILE, TILE, TILE))

        p_selected = board[y][x]
        for mx, my in valid_moves:
            target_piece = board[my][mx]
            is_capture = target_piece != ""
            
            # Controllo En Passant
            if p_selected and p_selected[1] == "p" and mx != x and target_piece == "":
                is_capture = True 
                target_piece = board[y][mx]

            # Scelta Colore
            if p_selected and p_selected[1] == "k" and abs(mx - x) == 2:
                # Arrocco (Verde Chiaro Speciale)
                color = CASTLE_LIGHT if (mx + my) % 2 == 0 else CASTLE_DARK
            elif is_capture:
                if target_piece != "" and target_piece[1] == "k":
                    color = KING_CAPT_LIGHT if (mx + my) % 2 == 0 else KING_CAPT_DARK
                else:
                    color = CAPT_LIGHT if (mx + my) % 2 == 0 else CAPT_DARK
            else:
                color = MOVE_LIGHT if (mx + my) % 2 == 0 else MOVE_DARK

            pygame.draw.rect(screen, color, (OFFSET_X + mx * TILE, OFFSET_Y + my * TILE, TILE, TILE))

def draw_board():
    bg = BG_WHITE if turn == "w" else BG_BLACK
    screen.fill(bg)
    
    pygame.draw.rect(screen, BOARD_BORDER_COLOR, (
        OFFSET_X - BORDER_THICKNESS, OFFSET_Y - BORDER_THICKNESS, 
        BOARD_SIZE + (BORDER_THICKNESS * 2), BOARD_SIZE + (BORDER_THICKNESS * 2)
    ))
    
    # 1. Disegna le caselle base
    for y in range(8):
        for x in range(8):
            color = LIGHT if (x+y)%2==0 else DARK
            pygame.draw.rect(screen, color, (OFFSET_X + x*TILE, OFFSET_Y + y*TILE, TILE, TILE))
            
    # 2. Sovrascrive di Rosso le caselle dello scacco se presente
    check_path = get_check_path(turn)
    for cx, cy in check_path:
        r_color = CHECK_RED_LIGHT if (cx + cy) % 2 == 0 else CHECK_RED_DARK
        pygame.draw.rect(screen, r_color, (OFFSET_X + cx*TILE, OFFSET_Y + cy*TILE, TILE, TILE))

def draw_pieces():
    for y in range(8):
        for x in range(8):
            p = board[y][x]
            if p != "" and p in PIECE_IMAGES:
                screen.blit(
                    PIECE_IMAGES[p], 
                    (OFFSET_X + x * TILE + PIECE_OFFSET, OFFSET_Y + y * TILE + PIECE_OFFSET)
                )

def check_king():
    w = b = False
    for row in board:
        for p in row:
            if p == "wk": w = True
            if p == "bk": b = True
    return w, b

# ---------------- LOOP PRINCIPALE ----------------
running = True

while running:
    clock.tick(60)

    if game_state == "MENU":
        draw_main_menu()
    elif game_state == "GAME":
        draw_board()
        draw_highlights() 
        draw_pieces()

        if not game_over:
            w, b = check_king()
            if not w: game_over = True; winner = "BLACK WINS"
            if not b: game_over = True; winner = "WHITE WINS"
        
        if game_over:
            draw_win_screen(winner)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            if game_state == "MENU":
                if play_rect and play_rect.collidepoint((mx, my)):
                    reset_game()
                    game_state = "GAME"
                elif quit_rect and quit_rect.collidepoint((mx, my)):
                    running = False
            
            elif game_state == "GAME":
                if game_over:
                    if rematch_rect and rematch_rect.collidepoint((mx, my)):
                        reset_game()
                    elif win_quit_rect and win_quit_rect.collidepoint((mx, my)):
                        running = False
                else:
                    x = (mx - OFFSET_X)//TILE
                    y = (my - OFFSET_Y)//TILE

                    if 0 <= x < 8 and 0 <= y < 8:
                        if selected:
                            x1, y1 = selected
                            piece = board[y1][x1]

                            if valid_move(x1, y1, x, y):
                                # Tracciamento movimento per Arrocco
                                if piece == "wk": has_moved["wk"] = True
                                if piece == "bk": has_moved["bk"] = True
                                if piece == "wr" and x1 == 0 and y1 == 7: has_moved["wr_l"] = True
                                if piece == "wr" and x1 == 7 and y1 == 7: has_moved["wr_r"] = True
                                if piece == "br" and x1 == 0 and y1 == 0: has_moved["br_l"] = True
                                if piece == "br" and x1 == 7 and y1 == 0: has_moved["br_r"] = True
                                
                                # Esecuzione Arrocco (sposta anche la torre)
                                if piece[1] == "k" and abs(x - x1) == 2:
                                    if x > x1: # Corto
                                        board[y][5] = board[y][7]
                                        board[y][7] = ""
                                    else: # Lungo
                                        board[y][3] = board[y][0]
                                        board[y][0] = ""

                                # En Passant
                                if piece[1] == "p" and abs(x - x1) == 1 and board[y][x] == "":
                                    board[y1][x] = ""

                                # Movimento normale
                                board[y][x] = piece
                                board[y1][x1] = ""

                                # Promozione Pedone
                                if piece[1] == "p" and (y == 0 or y == 7):
                                    board[y][x] = piece[0] + "q"

                                # Controllo doppio passo pedone (per En Passant futuro)
                                if piece[1] == "p" and abs(y - y1) == 2:
                                    last_double_pawn = (x, y, piece[0])
                                else:
                                    last_double_pawn = None

                                turn = "b" if turn == "w" else "w"

                            selected = None
                            valid_moves = []
                        else:
                            if board[y][x] != "" and board[y][x][0] == turn:
                                selected = (x, y)
                                valid_moves = [(i, j) for i in range(8) for j in range(8) if valid_move(x, y, i, j)]

    pygame.display.flip()

pygame.quit()
