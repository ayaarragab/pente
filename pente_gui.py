from pente import *
import pygame
from pygame.locals import *

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WOODEN = (210, 180, 140)
STONE_COLORS = {1: BLACK, 2: WHITE}
BOARD_SIZE = 19
CELL_SIZE = 30
MARGIN = 40
STONE_RADIUS = 12
SCREEN_SIZE = MARGIN * 2 + (BOARD_SIZE - 1) * CELL_SIZE

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Pente Game")
font = pygame.font.SysFont('Calibri', 30)

# Initialize game and AI
pente_game = PenteGame()
ai = PenteAI(pente_game, player_number=2)

# Helper functions
def draw_board():
    screen.fill(WOODEN)
    for row in range(BOARD_SIZE):
        pygame.draw.line(
            screen, BLACK,
            (MARGIN, MARGIN + row * CELL_SIZE),
            (MARGIN + (BOARD_SIZE - 1) * CELL_SIZE, MARGIN + row * CELL_SIZE),
            1
        )
    for col in range(BOARD_SIZE):
        pygame.draw.line(
            screen, BLACK,
            (MARGIN + col * CELL_SIZE, MARGIN),
            (MARGIN + col * CELL_SIZE, MARGIN + (BOARD_SIZE - 1) * CELL_SIZE),
            1
        )

def draw_stones():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            stone = pente_game.board[row][col]
            if stone != 0:
                pygame.draw.circle(
                    screen, STONE_COLORS[stone],
                    (MARGIN + col * CELL_SIZE, MARGIN + row * CELL_SIZE),
                    STONE_RADIUS
                )

def display_winner(winner):
    winner_text = font.render(f"Player {winner} wins!", True, BLACK)
    screen.blit(winner_text, (SCREEN_SIZE // 2 - winner_text.get_width() // 2, SCREEN_SIZE // 2 - 20))


def reset_game():
    global pente_game, ai, winner
    pente_game = PenteGame()
    ai = PenteAI(pente_game, player_number=2)
    winner = None


# Ensure the game instance is created properly
pente_game = PenteGame()
ai = PenteAI(pente_game, player_number=2)  # AI setup

# Main game loop
running = True
winner = None

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # Human turn
        if event.type == MOUSEBUTTONDOWN and winner is None and pente_game.current_player == 1:
            x, y = event.pos
            col = (x - MARGIN + CELL_SIZE // 2) // CELL_SIZE
            row = (y - MARGIN + CELL_SIZE // 2) // CELL_SIZE

            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                if pente_game.make_move(row, col):  # Human move
                    print(f"Player 1 made a move at ({row}, {col})")
                    winner = pente_game.check_win()
                    print(f"winner{winner}")

                    # Trigger AI turn if no winner
                    if winner is None:
                        # Update current player and perform AI move
                        print("AI's turn to move")
                        ai_move = ai.get_best_move()
                        if ai_move:  # Ensure AI has a valid move
                            pente_game.make_move(ai_move[0], ai_move[1])
                            print(f"AI played at {ai_move}")
                        else:
                            print("AI could not find a valid move.")
                        winner = pente_game.check_win()

    # Drawing
    draw_board()
    draw_stones()

    if winner:
        display_winner(winner)

    pygame.display.flip()

pygame.quit()
