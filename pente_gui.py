import pygame
from pygame.locals import *
from pente import PenteGame, PenteAI

class PenteGameGUI:
    # Constants
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    WOODEN = (210, 180, 140)
    GRAY = (128, 128, 128)
    STONE_COLORS = {1: BLACK, 2: WHITE}
    
    def __init__(self, board_size=19, cell_size=30, margin=40):
        # Game configuration
        self.BOARD_SIZE = board_size
        self.CELL_SIZE = cell_size
        self.MARGIN = margin
        self.STONE_RADIUS = 12
        self.SCREEN_SIZE = self.MARGIN * 2 + (self.BOARD_SIZE - 1) * self.CELL_SIZE + 200  # Extra width for captures

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_SIZE, self.SCREEN_SIZE))
        pygame.display.set_caption("Pente Game")
        
        # Fonts
        self.title_font = pygame.font.SysFont('Calibri', 30, bold=True)
        self.font = pygame.font.SysFont('Calibri', 24)

        # Game logic
        self.pente_game = PenteGame()
        self.ai = PenteAI(self.pente_game, player_number=2)
        self.winner = None

    def draw_board(self):
        """Draw the game board grid"""
        self.screen.fill(self.WOODEN)
        
        # Draw grid lines
        for row in range(self.BOARD_SIZE):
            pygame.draw.line(
                self.screen, self.BLACK,
                (self.MARGIN, self.MARGIN + row * self.CELL_SIZE),
                (self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL_SIZE, self.MARGIN + row * self.CELL_SIZE),
                1
            )
        for col in range(self.BOARD_SIZE):
            pygame.draw.line(
                self.screen, self.BLACK,
                (self.MARGIN + col * self.CELL_SIZE, self.MARGIN),
                (self.MARGIN + col * self.CELL_SIZE, self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL_SIZE),
                1
            )

    def draw_stones(self):
        """Draw stones on the board"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                stone = self.pente_game.board[row][col]
                if stone != 0:
                    pygame.draw.circle(
                        self.screen, self.STONE_COLORS[stone],
                        (self.MARGIN + col * self.CELL_SIZE, self.MARGIN + row * self.CELL_SIZE),
                        self.STONE_RADIUS
                    )

    def reset_game(self):
        """Reset the game state"""
        self.pente_game = PenteGame()
        self.ai = PenteAI(self.pente_game, player_number=2)
        self.winner = None

    def get_board_coordinates(self, mouse_pos):
        """Convert mouse position to board coordinates"""
        x, y = mouse_pos
        col = (x - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        row = (y - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        return row, col

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == MOUSEBUTTONDOWN and not self.winner:
                    # Human player's turn
                    if self.pente_game.current_player == 1:
                        try:
                            row, col = self.get_board_coordinates(event.pos)
                            if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE:
                                if self.pente_game.make_move(row, col):
                                    self.winner = self.pente_game.check_win()

                                    # AI's turn
                                    if not self.winner:
                                        ai_move = self.ai.get_best_move()
                                        if ai_move:
                                            self.pente_game.make_move(ai_move[0], ai_move[1])
                                            self.winner = self.pente_game.check_win()
                        except Exception as e:
                            print(f"Invalid move: {e}")

            self.draw_board()
            self.draw_stones()
            self.draw_captures()

            if self.winner:
                self.display_winner(self.winner)

            pygame.display.flip()

        pygame.quit()

    def draw_captures(self):
        """Draw capture information for both players"""
        captures_surface = pygame.Surface((200, 150), pygame.SRCALPHA)
        
        # Title
        title = self.title_font.render("Captures", True, self.BLACK)
        captures_surface.blit(title, (10, 10))

        # Player 1 captures
        captures_surface.fill(self.GRAY, rect=(10, 50, 80, 80))
        player1_text = self.font.render("Player 1", True, self.WHITE)
        captures_surface.blit(player1_text, (10, 35))
        player1_captures = self.font.render(str(self.pente_game.captures_p1), True, self.WHITE)
        captures_surface.blit(player1_captures, (40, 80))

        # Player 2 (AI) captures
        captures_surface.fill(self.GRAY, rect=(110, 50, 80, 80))
        player2_text = self.font.render("Player 2", True, self.WHITE)
        captures_surface.blit(player2_text, (110, 35))
        player2_captures = self.font.render(str(self.pente_game.captures_p2), True, self.WHITE)
        captures_surface.blit(player2_captures, (140, 80))

        # Blit the captures surface onto the main screen
        self.screen.blit(captures_surface, (self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL_SIZE + 20, 20))

    def display_winner(self, winner):
        """Display the winner of the game with enhanced appearance"""

        # Dim the screen by overlaying a semi-transparent black rectangle
        overlay = pygame.Surface((self.SCREEN_SIZE, self.SCREEN_SIZE))
        overlay.set_alpha(150)  # Adjust alpha for transparency
        overlay.fill((0, 0, 0))  # Black color
        self.screen.blit(overlay, (0, 0))

        # Larger fonts and white text for visibility
        large_title_font = pygame.font.Font(None, 100)  # Adjust as needed
        large_font = pygame.font.Font(None, 50)

        # Render winner text
        winner_text = large_title_font.render(f"Player {winner} wins!", True, (255, 255, 255))  # White color
        winner_text_rect = winner_text.get_rect(center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 - 60))
        self.screen.blit(winner_text, winner_text_rect)

        # Render reset instructions
        reset_text = large_font.render("Click to reset the game", True, (200, 200, 200))  # Light gray
        reset_text_rect = reset_text.get_rect(center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 + 60))
        self.screen.blit(reset_text, reset_text_rect)


def main():
    game = PenteGameGUI()
    game.run()

if __name__ == "__main__":
    main()
