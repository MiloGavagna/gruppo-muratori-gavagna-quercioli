import pygame
import os
import sys
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

# Dimensione base dei pezzi e offset di centratura
PIECE_SIZE = int(TILE * 0.90)
PIECE_OFFSET = (TILE - PIECE_SIZE) // 2

MENU_GRID_OFFSET_X = 25
MENU_GRID_OFFSET_Y = 25

# ---------------- PERCORSI DINAMICI INFALLIBILI (ANTI-BUG) ----------------
# Trova la cartella esatta in cui risiede questo file di script
CARTELLA_BASE = os.path.dirname(os.path.abspath(__file__))
# Crea il percorso sicuro verso la cartella "assets"
CARTELLA_ASSETS = os.path.join(CARTELLA_BASE, "assets")

# ---------------- SISTEMA SKIN (COLORI) ----------------
SKINS = ["classic", "woody"]
current_skin_idx = 0

SKIN_COLORS = {
    "classic": {
        "light": (200, 200, 200),
        "dark": (120, 120, 120),
        "border": (70, 70, 70),
        "bg_w": (240, 240, 240),
        "bg_b": (30, 30, 30)
    },
    "woody": {
        "light": (210, 180, 140),   # Legno chiaro
        "dark": (139, 69, 19),      # Legno scuro
        "border": (92, 58, 33),     # Marrone molto scuro
        "bg_w": (175, 165, 150),    # Marrone molto desaturato
        "bg_b": (80, 70, 60)        # Marrone scuro molto desaturato
    }
}

# ---------------- COLORI DI SISTEMA ----------------
SELECT_LIGHT = (190, 235, 255)   
SELECT_DARK = (110, 180, 220)     
MOVE_LIGHT = (170, 225, 255)      
MOVE_DARK = (90, 170, 210)       
CAPT_LIGHT = (255, 255, 170)      
CAPT_DARK = (195, 195, 80)        
KING_CAPT_LIGHT = (144, 238, 144) 
KING_CAPT_DARK = (60, 179, 113)   
CASTLE_LIGHT = (160, 255, 160)
CASTLE_DARK = (90, 200, 90)
CHECK_RED_LIGHT = (255, 120, 120)
CHECK_RED_DARK = (220, 80, 80)

WHITE = (255, 255, 255)
YELLOW = (255, 235, 120)
QUIT_RED = (180, 70, 70)            
GREEN_TEXT = (144, 238, 144)     
CREDITS_GRAY = (180, 180, 180)

# ---------------- FONT DI SISTEMA ----------------
font_small = pygame.font.SysFont("impact", 30)
font = pygame.font.SysFont("impact", 50)
font_big = pygame.font.SysFont("impact", 75)
font_title = pygame.font.SysFont("impact", 110)

# ---------------- CARICAMENTO ASSET PNG CON CONTROLLO PERCORSI ----------------
PIECE_IMAGES = {"classic": {}, "woody": {}}
pieces_names = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]

piece_names_map = {"p": "pawn", "r": "tower", "n": "knight", "b": "bishop", "q": "queen", "k": "king"}
color_names_map = {"w": "white", "b": "black"}

for skin in SKINS:
    target_size = PIECE_SIZE
    if skin == "woody":
        target_size = int(PIECE_SIZE * 1.20)
        
    for name in pieces_names:
        color_str = color_names_map[name[0]]
        piece_str = piece_names_map[name[1]]
        filename = f"spr_{piece_str}_{color_str}.png"
        
        # Costruisce il percorso assoluto dinamico specifico per la skin corrente
        path = os.path.join(CARTELLA_ASSETS, skin, filename)
        
        try:
            img = pygame.image.load(path).convert_alpha()
            PIECE_IMAGES[skin][name] = pygame.transform.scale(img, (target_size, target_size))
        except FileNotFoundError:
            print(f"⚠️ ATTENZIONE: Immagine '{filename}' non trovata per la skin '{skin}'!")
            print(f"Percorso cercato: {path}")
            print("Controlla che i file grafici siano dentro la cartella degli asset.")

# ---------------- VARIABILI DI STATO GLOBALI ----------------
board = []
selected = None
valid_moves = []
turn = "w"
game_over = False
winner = ""
last_double_pawn = None

game_state = "MENU"       
game_mode = "STANDARD"    

play_rect = None
skin_rect = None
quit_rect = None
standard_rect = None
chaos_rect = None
rematch_rect = None
win_quit_rect = None
win_menu_rect = None
ingame_menu_rect = None   # Nuovo rettangolo per il tasto "M" in gioco

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
    
    if game_mode == "STANDARD":
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
    else: 
        b_types = [random.choice(['p', 'r', 'n', 'b', 'q', 'k']) for _ in range(16)]
        if 'k' not in b_types:
            b_types[random.randint(0, 15)] = 'k'
        b_pieces = ['b' + t for t in b_types]
        
        w_types = [random.choice(['p', 'r', 'n', 'b', 'q', 'k']) for _ in range(16)]
        if 'k' not in w_types:
            w_types[random.randint(0, 15)] = 'k'
        w_pieces = ['w' + t for t in w_types]
        
        board = [
            b_pieces[0:8],
            b_pieces[8:16],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            w_pieces[0:8],
            w_pieces[8:16]
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

# ---------------- SCHERMATE DI MENU ----------------
def draw_menu_base():
    skin_name = SKINS[current_skin_idx]
    colors = SKIN_COLORS[skin_name]
    
    # Calcoliamo la dimensione corretta del pezzo in base alla skin (identico a draw_pieces)
    target_size = PIECE_SIZE
    if skin_name == "woody":
        target_size = int(PIECE_SIZE * 1.20)
        
    # Calcoliamo l'offset di centratura dinamico per la griglia del menu
    tile_w = WIDTH // 8
    tile_h = HEIGHT // 8
    offset_center_x = (tile_w - target_size) // 2
    offset_center_y = (tile_h - target_size) // 2

    # Disegna la scacchiera di sfondo
    for y in range(-1, 9): 
        for x in range(-1, 9):
            color = colors["light"] if (x+y)%2==0 else colors["dark"]
            pygame.draw.rect(screen, color, (x * tile_w + MENU_GRID_OFFSET_X, y * tile_h + MENU_GRID_OFFSET_Y, tile_w, tile_h))
            
    # Disegna i pezzi decorativi di sfondo ben centrati e della scala corretta
    for rx, ry, r_piece in menu_bg_pieces:
        if r_piece in PIECE_IMAGES[skin_name]:
            px = rx * tile_w + MENU_GRID_OFFSET_X + offset_center_x
            py = ry * tile_h + MENU_GRID_OFFSET_Y + offset_center_y
            screen.blit(PIECE_IMAGES[skin_name][r_piece], (px, py))
            
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))
    
    title_surf = font_title.render("SCACCOMATTO", True, YELLOW)
    title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 90))
    screen.blit(title_surf, title_rect)

def draw_main_menu():
    global play_rect, skin_rect, quit_rect
    draw_menu_base()
    
    play_surf = font.render("- Play -", True, WHITE)
    play_rect = play_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    screen.blit(play_surf, play_rect)
    
    skin_display_name = SKINS[current_skin_idx].capitalize()
    skin_surf = font.render(f"- Skin: {skin_display_name} -", True, WHITE)
    skin_rect = skin_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
    screen.blit(skin_surf, skin_rect)
    
    quit_surf = font.render("- Quit -", True, QUIT_RED)
    quit_rect = quit_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 160))
    screen.blit(quit_surf, quit_rect)
    
    credits_surf = font_small.render("by Mc Quer Albus Studios", True, CREDITS_GRAY)
    credits_rect = credits_surf.get_rect(bottomleft=(30, HEIGHT - 30))
    screen.blit(credits_surf, credits_rect)

def draw_mode_menu():
    global standard_rect, chaos_rect
    draw_menu_base() 
    
    standard_surf = font.render("- Standard -", True, WHITE)
    standard_rect = standard_surf.get_rect(center=(WIDTH//2 - 140, HEIGHT//2 + 40))
    screen.blit(standard_surf, standard_rect)
    
    chaos_surf = font.render("- Chaos -", True, CHECK_RED_LIGHT)
    chaos_rect = chaos_surf.get_rect(center=(WIDTH//2 + 140, HEIGHT//2 + 40))
    screen.blit(chaos_surf, chaos_rect)

# ---------------- WIN SCREEN ----------------
def draw_win_screen(winner_text):
    global rematch_rect, win_quit_rect, win_menu_rect
    
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

    win_menu_surf = font_small.render("- Menu -", True, WHITE)
    win_menu_rect = win_menu_surf.get_rect(bottomleft=(30, HEIGHT - 30))
    screen.blit(win_menu_surf, win_menu_rect)

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
    for y in range(8):
        for x in range(8):
            p = board[y][x]
            if p != "" and p[0] != color:
                if attacks_square(x, y, tx, ty, p): return True
    return False

def get_check_path(color):
    path = []
    kings_positions = []
    for y in range(8):
        for x in range(8):
            if board[y][x] == color + "k":
                kings_positions.append((x, y))
                
    for kx, ky in kings_positions:
        for y in range(8):
            for x in range(8):
                p = board[y][x]
                if p != "" and p[0] != color:
                    if attacks_square(x, y, kx, ky, p):
                        if (kx, ky) not in path: path.append((kx, ky))
                        if (x, y) not in path: path.append((x, y))
                        if p[1] in ['r', 'b', 'q']:
                            dx, dy = kx - x, ky - y
                            step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
                            step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
                            cx, cy = x + step_x, y + step_y
                            while (cx, cy) != (kx, ky):
                                if (cx, cy) not in path: path.append((cx, cy))
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

    if kind == "k" and abs(dx) == 2 and dy == 0 and game_mode == "STANDARD":
        row = 7 if color == "w" else 0
        if y1 != row or y2 != row: return False
        if dx == 2: 
            rook_key = "wr_r" if color == "w" else "br_r"
            if not has_moved[color + "k"] and not has_moved.get(rook_key, False):
                if board[row][5] == "" and board[row][6] == "":
                    if not is_under_attack(4, row, color) and not is_under_attack(5, row, color) and not is_under_attack(6, row, color):
                        return True
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

# ---------------- RENDERING GRAFICA DI GIOCO ----------------
def draw_highlights():
    if selected:
        x, y = selected
        sel_color = SELECT_LIGHT if (x + y) % 2 == 0 else SELECT_DARK
        pygame.draw.rect(screen, sel_color, (OFFSET_X + x * TILE, OFFSET_Y + y * TILE, TILE, TILE))

        p_selected = board[y][x]
        for mx, my in valid_moves:
            target_piece = board[my][mx]
            is_capture = target_piece != ""
            
            if p_selected and p_selected[1] == "p" and mx != x and target_piece == "":
                is_capture = True 
                target_piece = board[y][mx]

            if p_selected and p_selected[1] == "k" and abs(mx - x) == 2:
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
    skin_name = SKINS[current_skin_idx]
    colors = SKIN_COLORS[skin_name]
    
    bg = colors["bg_w"] if turn == "w" else colors["bg_b"]
    screen.fill(bg)
    
    pygame.draw.rect(screen, colors["border"], (
        OFFSET_X - BORDER_THICKNESS, OFFSET_Y - BORDER_THICKNESS, 
        BOARD_SIZE + (BORDER_THICKNESS * 2), BOARD_SIZE + (BORDER_THICKNESS * 2)
    ))
    
    for y in range(8):
        for x in range(8):
            color = colors["light"] if (x+y)%2==0 else colors["dark"]
            pygame.draw.rect(screen, color, (OFFSET_X + x*TILE, OFFSET_Y + y*TILE, TILE, TILE))
            
    check_path = get_check_path(turn)
    for cx, cy in check_path:
        r_color = CHECK_RED_LIGHT if (cx + cy) % 2 == 0 else CHECK_RED_DARK
        pygame.draw.rect(screen, r_color, (OFFSET_X + cx*TILE, OFFSET_Y + cy*TILE, TILE, TILE))

def draw_pieces():
    skin_name = SKINS[current_skin_idx]
    
    OFFSET_CENTER = PIECE_OFFSET
    if skin_name == "woody" and "wp" in PIECE_IMAGES["woody"]:
        OFFSET_CENTER = (TILE - PIECE_IMAGES["woody"]["wp"].get_width()) // 2
        
    for y in range(8):
        for x in range(8):
            p = board[y][x]
            if p != "" and p in PIECE_IMAGES[skin_name]:
                screen.blit(
                    PIECE_IMAGES[skin_name][p], 
                    (OFFSET_X + x * TILE + OFFSET_CENTER, OFFSET_Y + y * TILE + OFFSET_CENTER)
                )

def check_king():
    w = b = False
    for row in board:
        for p in row:
            if p == "wk": w = True
            if p == "bk": b = True
    return w, b

# ---------------- LOOP PRINCIPALE GIOCO ----------------
running = True

while running:
    clock.tick(60)

    if game_state == "MENU":
        draw_main_menu()
    elif game_state == "MODE_MENU":
        draw_mode_menu()
    elif game_state == "GAME":
        draw_board()
        draw_highlights() 
        draw_pieces()

        if not game_over:
            w, b = check_king()
            if not w: game_over = True; winner = "BLACK WINS"
            if not b: game_over = True; winner = "WHITE WINS"
            
            # Disegna il tasto "M" in basso a sinistra mentre la partita è in corso
            ingame_menu_surf = font.render("m", True, WHITE)
            ingame_menu_rect = ingame_menu_surf.get_rect(bottomleft=(10, HEIGHT - 10))
            screen.blit(ingame_menu_surf, ingame_menu_rect)
        
        if game_over:
            draw_win_screen(winner)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # 1. Click nello stato MENU PRINCIPALE
            if game_state == "MENU":
                if play_rect and play_rect.collidepoint((mx, my)):
                    game_state = "MODE_MENU"
                elif skin_rect and skin_rect.collidepoint((mx, my)):
                    current_skin_idx = (current_skin_idx + 1) % len(SKINS)
                elif quit_rect and quit_rect.collidepoint((mx, my)):
                    running = False
            
            # 2. Click nello stato MENU SELEZIONE MODALITÀ
            elif game_state == "MODE_MENU":
                if standard_rect and standard_rect.collidepoint((mx, my)):
                    game_mode = "STANDARD"
                    reset_game()
                    game_state = "GAME"
                elif chaos_rect and chaos_rect.collidepoint((mx, my)):
                    game_mode = "CHAOS"
                    reset_game()
                    game_state = "GAME"
            
            # 3. Click nello stato GAMEPLAY / FINE PARTITA
            elif game_state == "GAME":
                if game_over:
                    if rematch_rect and rematch_rect.collidepoint((mx, my)):
                        reset_game()
                    elif win_quit_rect and win_quit_rect.collidepoint((mx, my)):
                        running = False
                    elif win_menu_rect and win_menu_rect.collidepoint((mx, my)):
                        generate_menu_background()
                        game_state = "MENU"
                else:
                    # Controllo se è stato cliccato il tasto "M"
                    if ingame_menu_rect and ingame_menu_rect.collidepoint((mx, my)):
                        generate_menu_background()
                        game_state = "MENU"
                    else:
                        x = (mx - OFFSET_X)//TILE
                        y = (my - OFFSET_Y)//TILE

                        if 0 <= x < 8 and 0 <= y < 8:
                            if selected:
                                x1, y1 = selected
                                piece = board[y1][x1]

                                if valid_move(x1, y1, x, y):
                                    if piece == "wk": has_moved["wk"] = True
                                    if piece == "bk": has_moved["bk"] = True
                                    if piece == "wr" and x1 == 0 and y1 == 7: has_moved["wr_l"] = True
                                    if piece == "wr" and x1 == 7 and y1 == 7: has_moved["wr_r"] = True
                                    if piece == "br" and x1 == 0 and y1 == 0: has_moved["br_l"] = True
                                    if piece == "br" and x1 == 7 and y1 == 0: has_moved["br_r"] = True
                                    
                                    if piece[1] == "k" and abs(x - x1) == 2:
                                        if x > x1: 
                                            board[y][5] = board[y][7]; board[y][7] = ""
                                        else: 
                                            board[y][3] = board[y][0]; board[y][0] = ""

                                    if piece[1] == "p" and abs(x - x1) == 1 and board[y][x] == "":
                                        board[y1][x] = ""

                                    board[y][x] = piece
                                    board[y1][x1] = ""

                                    if piece[1] == "p" and (y == 0 or y == 7):
                                        board[y][x] = piece[0] + "q"

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