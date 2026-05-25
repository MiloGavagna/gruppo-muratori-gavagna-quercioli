import pygame

pygame.init()

# ---------------- DISPLAY ----------------
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Improved")

BOARD_SIZE = 560
TILE = BOARD_SIZE // 8

OFFSET_X = (WIDTH - BOARD_SIZE) // 2
OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2

# ---------------- COLORS ----------------
BG = (15, 50, 35)          # verde scuro sfondo
LIGHT = (235, 210, 170)    # caselle chiare legno
DARK = (160, 110, 70)      # caselle scure legno

HIGHLIGHT_LIGHT = (255, 255, 140)  # giallo chiaro
HIGHLIGHT_DARK = (200, 200, 90)    # giallo scuro

SELECT = (255, 255, 0)

# ---------------- BOARD ----------------
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

# ---------------- PIECES (LETTERS) ----------------
letters = {
    "wp":"P","wr":"R","wn":"N","wb":"B","wq":"Q","wk":"K",
    "bp":"P","br":"R","bn":"N","bb":"B","bq":"Q","bk":"K"
}

selected = None
valid_moves = []
turn = "w"
game_over = False
winner = ""

font = pygame.font.SysFont(None, 40)
font_big = pygame.font.SysFont(None, 60)

# ---------------- DRAW BOARD ----------------
def draw_board():
    screen.fill(BG)

    for y in range(8):
        for x in range(8):
            base = LIGHT if (x+y)%2==0 else DARK
            pygame.draw.rect(
                screen,
                base,
                (OFFSET_X + x*TILE, OFFSET_Y + y*TILE, TILE, TILE)
            )

# ---------------- DRAW PIECES ----------------
def draw_pieces():
    for y in range(8):
        for x in range(8):
            p = board[y][x]
            if p != "":
                text = font.render(letters[p], True, (0,0,0))
                screen.blit(
                    text,
                    (OFFSET_X + x*TILE + TILE//3, OFFSET_Y + y*TILE + TILE//4)
                )

# ---------------- MOVE VALIDATION ----------------
def valid_move(x1,y1,x2,y2):
    piece = board[y1][x1]
    if piece == "":
        return False

    color = piece[0]
    kind = piece[1]
    target = board[y2][x2]

    if target != "" and target[0] == color:
        return False

    dx = x2 - x1
    dy = y2 - y1

    # PAWN
    if kind == "p":
        direction = -1 if color == "w" else 1

        if dx == 0 and target == "":
            if dy == direction:
                return True
            if (y1 == 6 and color == "w") or (y1 == 1 and color == "b"):
                if dy == 2*direction and board[y1+direction][x1] == "":
                    return True

        if abs(dx) == 1 and dy == direction and target != "":
            return True

    # ROOK
    if kind == "r":
        if dx == 0 or dy == 0:
            return True

    # BISHOP
    if kind == "b":
        if abs(dx) == abs(dy):
            return True

    # QUEEN
    if kind == "q":
        if dx == 0 or dy == 0 or abs(dx) == abs(dy):
            return True

    # KNIGHT
    if kind == "n":
        if (abs(dx), abs(dy)) in [(1,2),(2,1)]:
            return True

    # KING
    if kind == "k":
        if abs(dx) <= 1 and abs(dy) <= 1:
            return True

    return False

# ---------------- HIGHLIGHTS ----------------
def draw_highlights():
    if selected:
        x,y = selected

        for mx,my in valid_moves:
            base = LIGHT if (mx+my)%2==0 else DARK
            color = HIGHLIGHT_LIGHT if base == LIGHT else HIGHLIGHT_DARK

            pygame.draw.rect(
                screen,
                color,
                (OFFSET_X + mx*TILE, OFFSET_Y + my*TILE, TILE, TILE)
            )

        pygame.draw.rect(
            screen,
            SELECT,
            (OFFSET_X + x*TILE, OFFSET_Y + y*TILE, TILE, TILE),
            3
        )

# ---------------- CHECK WIN ----------------
def check_king():
    w = False
    b = False
    for row in board:
        for p in row:
            if p == "wk":
                w = True
            if p == "bk":
                b = True
    return w,b

# ---------------- LOOP ----------------
running = True

while running:
    clock = pygame.time.Clock()
    clock.tick(60)

    draw_board()
    draw_highlights()
    draw_pieces()

    w,b = check_king()

    if not w:
        game_over = True
        winner = "BLACK WINS"
    if not b:
        game_over = True
        winner = "WHITE WINS"

    if game_over:
        text = font_big.render(winner, True, (255,255,255))
        screen.blit(text, (200, 300))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()

            x = (mx - OFFSET_X)//TILE
            y = (my - OFFSET_Y)//TILE

            if 0 <= x < 8 and 0 <= y < 8:

                if selected:
                    x1,y1 = selected

                    if valid_move(x1,y1,x,y):
                        board[y][x] = board[y1][x1]
                        board[y1][x1] = ""

                    selected = None
                    valid_moves = []

                else:
                    if board[y][x] != "" and board[y][x][0] == turn:
                        selected = (x,y)

                        valid_moves = [
                            (i,j)
                            for i in range(8)
                            for j in range(8)
                            if valid_move(x,y,i,j)
                        ]

    pygame.display.flip()

pygame.quit()