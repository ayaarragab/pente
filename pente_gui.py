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
        self.pente_game = None
        self.ai = None
        self.winner = None
        self.current_algorithm = None
        self.current_difficulty = None

        self.show_algorithm_selection_screen()

    def create_button(self, text, x, y, width=200, height=60):
        """Helper method to create a button"""
        button_font = pygame.font.Font(None, 50)
        button = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (139, 69, 19), button, border_radius=10)  # Brown color
        pygame.draw.rect(self.screen, (0, 0, 0), button, 2, border_radius=10)  # Black border (shadow)

        button_text = button_font.render(text, True, (255, 255, 255))  # White text
        text_rect = button_text.get_rect(center=button.center)

        return button, text_rect, button_text

    def show_algorithm_selection_screen(self):
        """Display screen to select game algorithm"""
        self.screen.fill((245, 211, 161))  # Light brown background

        # Welcome text
        welcome_font = pygame.font.Font(None, 74)
        welcome_text = welcome_font.render("Select Algorithm", True, self.BLACK)
        welcome_rect = welcome_text.get_rect(center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 - 150))
        self.screen.blit(welcome_text, welcome_rect)

        alpha_beta_button, alpha_beta_text_rect, alpha_beta_text = self.create_button(
            "Alpha-Beta",
            self.SCREEN_SIZE // 2 - 250,
            self.SCREEN_SIZE // 2 - 40
        )
        min_max_button, min_max_text_rect, min_max_text = self.create_button(
            "Min-Max",
            self.SCREEN_SIZE // 2 + 50,
            self.SCREEN_SIZE // 2 - 40
        )

        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

                if event.type == MOUSEBUTTONDOWN:
                    if alpha_beta_button.collidepoint(event.pos):
                        self.current_algorithm = "Alpha-Beta"
                        running = False
                    elif min_max_button.collidepoint(event.pos):
                        self.current_algorithm = "Min-Max"
                        running = False

            self.screen.blit(alpha_beta_text, alpha_beta_text_rect)
            self.screen.blit(min_max_text, min_max_text_rect)
            pygame.display.flip()

        self.show_difficulty_selection_screen()

    def show_difficulty_selection_screen(self):
        """Display screen to select game difficulty"""
        self.screen.fill((245, 211, 161))  # Light brown background

        welcome_font = pygame.font.Font(None, 74)
        welcome_text = welcome_font.render(f"{self.current_algorithm} Difficulty", True, self.BLACK)
        welcome_rect = welcome_text.get_rect(center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 - 150))
        self.screen.blit(welcome_text, welcome_rect)

        easy_button, easy_text_rect, easy_text = self.create_button(
            "Easy",
            self.SCREEN_SIZE // 2 - 250,
            self.SCREEN_SIZE // 2 - 40
        )
        hard_button, hard_text_rect, hard_text = self.create_button(
            "Hard",
            self.SCREEN_SIZE // 2 + 50,
            self.SCREEN_SIZE // 2 - 40
        )

        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

                if event.type == MOUSEBUTTONDOWN:
                    if easy_button.collidepoint(event.pos):
                        self.current_difficulty = "Easy"
                        running = False
                    elif hard_button.collidepoint(event.pos):
                        self.current_difficulty = "Hard"
                        running = False

            # Draw buttons
            self.screen.blit(easy_text, easy_text_rect)
            self.screen.blit(hard_text, hard_text_rect)
            pygame.display.flip()

        self.start_game()

    def start_game(self):
        print(f"Starting game with {self.current_algorithm} algorithm on {self.current_difficulty} mode")

        # Initialize game logic
        self.pente_game = PenteGame()

        # heuristic
        heuristic_fun = (PenteAI.evaluate_board_state_advanced
                         if self.current_difficulty == "Hard"
                         else PenteAI.evaluate_board_state_easy)

        is_alpha_beta = self.current_algorithm == "Alpha-Beta"

        # Initialize AI
        self.ai = PenteAI(self.pente_game, player_number=2)

        self.heuristic_fun = heuristic_fun
        self.is_alpha_beta = is_alpha_beta

        self.winner = None
        self.run_game()

    def run_game(self):
        running = True
        while running:
            self.draw_board()
            self.draw_stones()
            self.draw_captures()

            if self.winner:
                self.display_winner(self.winner)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                if event.type == MOUSEBUTTONDOWN and not self.winner:
                    # Human turn
                    if self.pente_game.current_player == 1:
                        # try:
                            row, col = self.get_board_coordinates(event.pos)
                            if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE:
                                if self.pente_game.make_move(row, col):
                                    self.winner = self.pente_game.check_win()

                                    self.draw_board()
                                    self.draw_stones()
                                    self.draw_captures()
                                    pygame.display.flip()
                                    # ai turn
                                    if not self.winner:
                                        ai_move = self.ai.get_best_move(
                                            self.pente_game.board,
                                            minimax_func=(
                                                self.ai.minimax if self.is_alpha_beta else self.ai.minimax_without_alpha_Beta),
                                            isAlphaBeta=self.is_alpha_beta,
                                            heuristic_fun=self.heuristic_fun
                                        )
                                        if ai_move:
                                            self.pente_game.make_move(ai_move[0], ai_move[1])
                                            self.winner = self.pente_game.check_win()

                        # except Exception as e:
                        #     print(f"Invalid move: {e}")

        pygame.quit()

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

    def get_board_coordinates(self, mouse_pos):
        """Convert mouse position to board coordinates"""
        x, y = mouse_pos
        col = (x - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        row = (y - self.MARGIN + self.CELL_SIZE // 2) // self.CELL_SIZE
        return row, col

    def draw_captures(self):
        """Draw capture information for both players in a modern, spaced-out style"""
        captures_surface = pygame.Surface((250, 120), pygame.SRCALPHA)

        # Title
        title = self.title_font.render("Captures", True, (0, 0, 0))
        title_rect = title.get_rect(midtop=(125, 10))
        captures_surface.blit(title, title_rect)

        p1_box_rect = pygame.Rect(20, 40, 100, 100)
        pygame.draw.rect(captures_surface, (130, 69, 19), p1_box_rect, border_radius=10)  # Dark brown frame
        player1_text = self.font.render("Player 1", True, (255, 255, 255))
        player1_text_rect = player1_text.get_rect(midtop=(p1_box_rect.x + 50, p1_box_rect.y + 10))
        captures_surface.blit(player1_text, player1_text_rect)
        player1_captures = self.font.render(str(self.pente_game.captures_p1), True, (255, 255, 255))
        player1_captures_rect = player1_captures.get_rect(center=(p1_box_rect.x + 50, p1_box_rect.y + 60))
        captures_surface.blit(player1_captures, player1_captures_rect)

        # Spacing between the boxes
        spacing = 10

        p2_box_rect = pygame.Rect(p1_box_rect.right + spacing, 40, 100, 100)
        pygame.draw.rect(captures_surface, (139, 69, 19), p2_box_rect, border_radius=10)
        player2_text = self.font.render("Player 2", True, (255, 255, 255))
        player2_text_rect = player2_text.get_rect(midtop=(p2_box_rect.x + 50, p2_box_rect.y + 10))
        captures_surface.blit(player2_text, player2_text_rect)
        player2_captures = self.font.render(str(self.pente_game.captures_p2), True, (255, 255, 255))
        player2_captures_rect = player2_captures.get_rect(center=(p2_box_rect.x + 50, p2_box_rect.y + 60))
        captures_surface.blit(player2_captures, player2_captures_rect)

        self.screen.blit(captures_surface, (self.MARGIN + (self.BOARD_SIZE - 1) * self.CELL_SIZE + 20, 20))

    def display_winner(self, winner):
        """Display the winner and show reset and exit buttons."""
        overlay = pygame.Surface((self.SCREEN_SIZE, self.SCREEN_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        if winner == 1:
            winner_text = "You Win!"
        elif winner == 2:
            winner_text = "AI Wins!"
        else:
            winner_text = "Draw!"

        winner_font = pygame.font.Font(None, 74)
        text = winner_font.render(winner_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 - 100))
        self.screen.blit(text, text_rect)

        # Reset and Exit Buttons
        reset_button = pygame.Rect(self.SCREEN_SIZE // 2 - 150, self.SCREEN_SIZE // 2, 120, 50)
        exit_button = pygame.Rect(self.SCREEN_SIZE // 2 + 30, self.SCREEN_SIZE // 2, 120, 50)

        # Add shadow effect for buttons
        shadow_offset = 5
        pygame.draw.rect(self.screen, (50, 50, 50), reset_button.move(shadow_offset, shadow_offset), border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), exit_button.move(shadow_offset, shadow_offset), border_radius=10)

        # Draw buttons with brown color
        pygame.draw.rect(self.screen, (139, 69, 19), reset_button, border_radius=10)
        pygame.draw.rect(self.screen, (139, 69, 19), exit_button, border_radius=10)

        # Add black frame for buttons
        pygame.draw.rect(self.screen, self.BLACK, reset_button, 2, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, exit_button, 2, border_radius=10)

        # Add white text to buttons
        reset_text = self.font.render("Reset", True, self.WHITE)
        exit_text = self.font.render("Exit", True, self.WHITE)

        reset_text_rect = reset_text.get_rect(center=reset_button.center)
        exit_text_rect = exit_text.get_rect(center=exit_button.center)

        self.screen.blit(reset_text, reset_text_rect)
        self.screen.blit(exit_text, exit_text_rect)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

                if event.type == MOUSEBUTTONDOWN:
                    if reset_button.collidepoint(event.pos):
                        self.show_algorithm_selection_screen()
                        waiting = False
                    elif exit_button.collidepoint(event.pos):
                        pygame.quit()
                        exit()


game = PenteGameGUI()
