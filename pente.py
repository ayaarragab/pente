import time


class PenteGame:
    def __init__(self, board_size=19):
        """
        Initialize the Pente game board and game state

        Args:
            board_size (int): Size of the game board (default 19x19)
        """
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 1
        self.captures_p1 = 0
        self.captures_p2 = 0

    def is_valid_move(self, row, col):
        """
        Check if a move is valid

        Args:
            row (int): Row of the move
            col (int): Column of the move

        Returns:
            bool: True if move is valid, False otherwise
        """
        return (0 <= row < self.board_size and
                0 <= col < self.board_size and
                self.board[row][col] == 0)

    def make_move(self, row, col):
        if not self.is_valid_move(row, col):
            return False

        # Place the stone for the current player
        self.board[row][col] = self.current_player


        # Check for captures and update capture count
        captures = self.check_captures(row, col)
        if captures > 0:
            if self.current_player == 1:
                self.captures_p1 += captures
            elif self.current_player == 2:
                self.captures_p2 += captures

        # Switch to the other player
        self.toggle_player()

        print(f"Current player after move: {self.current_player}")  # Debugging line
        return True

    def toggle_player(self):
        """Switch the current player between 1 and 2."""
        self.current_player = 3 - self.current_player  # Alternates between 1 and 2
        print(f"Current player after toggle: {self.current_player}")  # Debugging line

    def check_captures(self, row, col):
        """
        Check and remove captured stone pairs

        Args:
            row (int): Row of the last placed stone
            col (int): Column of the last placed stone

        Returns:
            int: Number of stone pairs captured
        """
        directions = [
            (0, 1), (1, 0), (1, 1), (-1, 1),  # horizontal, vertical, diagonals
            (0, -1), (-1, 0), (-1, -1), (1, -1)
        ]

        total_captures = 0
        current_stone = self.board[row][col]
        opponent_stone = 3 - current_stone

        for dx, dy in directions:
            total_captures += self.check_direction_captures(row, col, dx, dy, current_stone, opponent_stone)

        return total_captures

    def check_direction_captures(self, row, col, dx, dy, current_stone, opponent_stone):
        """
        Check captures in a specific direction

        Args:
            row (int): Starting row
            col (int): Starting column
            dx (int): Row direction
            dy (int): Column direction
            current_stone (int): Current player's stone
            opponent_stone (int): Opponent's stone

        Returns:
            int: Number of captures in this direction
        """
        captures = 0
        try:
            # Check for opponent stones to capture
            if (self.board[row + dx][col + dy] == opponent_stone and
                    self.board[row + 2 * dx][col + 2 * dy] == opponent_stone and
                    self.board[row + 3 * dx][col + 3 * dy] == current_stone):
                # Remove captured stones
                self.board[row + dx][col + dy] = 0
                self.board[row + 2 * dx][col + 2 * dy] = 0
                captures = 1
        except IndexError:
            # Out of board bounds
            return 0

        return captures

    def check_win(self):
        """Check for win conditions."""
        for player in [1, 2]:
            # Check horizontal, vertical, and diagonal for a winning line
            for row in range(self.board_size):
                for col in range(self.board_size - 4):
                    if all(self.board[row][col + i] == player for i in range(5)):
                        return player
            for col in range(self.board_size):
                for row in range(self.board_size - 4):
                    if all(self.board[row + i][col] == player for i in range(5)):
                        return player
            for row in range(self.board_size - 4):
                for col in range(self.board_size - 4):
                    if all(self.board[row + i][col + i] == player for i in range(5)):
                        return player
                    if all(self.board[row + 4 - i][col + i] == player for i in range(5)):
                        return player

        # Check captures (5 captures) for a win
        if self.captures_p1 >= 5:
            return 1
        if self.captures_p2 >= 5:
            return 2

        return None  # Return None if no winner yet

class PenteAI:
    def __init__(self, game, player_number):
        """
        Initialize AI player

        Args:
            game (PenteGame): Game instance
            player_number (int): AI's player number (1 or 2)
        """
        self.game = game
        self.player_number = player_number
        self.opponent = 3 - player_number

    @staticmethod
    def evaluate_board_state(board, player): #heuristic funtion 1
        """
        Heuristic function for evaluating board state in a two-player game

        Args:
            board (list): Game board
            player (int): Current player number

        Returns:
            int: Evaluation score of the board state
        """
        opponent = 3 - player
        score = 0
        board_size = len(board)

        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1)
        ]

        patterns = {
            (player, player, player, player, player): 10000,  # Win
            (0, player, player, player, player, 0): 2000,  # Open four
            (player, player, player, player, 0): 800,  # Four
            (0, player, player, player, 0): 200,  # Open three
            (player, player, player, 0, 0): 50,  # Three
            (0, player, player, 0): 10,  # Open two
            (player, player, 0, 0): 5  # Two
        }

        # Check for captures (higher priority)
        captures = 0
        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == player:
                    for dx, dy in directions:
                        try:
                            if (0 <= row + 3 * dx < board_size and
                                    0 <= col + 3 * dy < board_size and
                                    board[row + dx][col + dy] == opponent and
                                    board[row + 2 * dx][col + 2 * dy] == opponent and
                                    board[row + 3 * dx][col + 3 * dy] == player):
                                captures += 1
                        except IndexError:
                            continue
        score += captures * 300

        # Pattern recognition
        for row in range(board_size):
            for col in range(board_size):
                for dx, dy in directions:
                    # Check each pattern
                    for pattern, pattern_score in patterns.items():
                        pattern_found = True
                        pattern_length = len(pattern)

                        # Verify pattern fits on board
                        if not (0 <= row + (pattern_length - 1) * dx < board_size and
                                0 <= col + (pattern_length - 1) * dy < board_size):
                            continue

                        # Check if pattern matches
                        for i, value in enumerate(pattern):
                            if board[row + i * dx][col + i * dy] != value:
                                pattern_found = False
                                break

                        if pattern_found:
                            score += pattern_score

        # Opponent patterns (defensive moves)
        opponent_patterns = {
            (opponent, opponent, opponent, opponent, 0): -900,  # Block opponent's four
            (0, opponent, opponent, opponent, 0): -300,  # Block opponent's open three
            (opponent, opponent, opponent, 0, 0): -80,  # Block opponent's three
            (0, opponent, opponent, 0): -20  # Block opponent's open two
        }

        # Check opponent patterns
        for row in range(board_size):
            for col in range(board_size):
                for dx, dy in directions:
                    for pattern, pattern_score in opponent_patterns.items():
                        pattern_found = True
                        pattern_length = len(pattern)

                        if not (0 <= row + (pattern_length - 1) * dx < board_size and
                                0 <= col + (pattern_length - 1) * dy < board_size):
                            continue

                        for i, value in enumerate(pattern):
                            if board[row + i * dx][col + i * dy] != value:
                                pattern_found = False
                                break

                        if pattern_found:
                            score += pattern_score

        # Position evaluation
        center = board_size // 2
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= center + i < board_size and 0 <= center + j < board_size:
                    if board[center + i][center + j] == player:
                        score += 5 - max(abs(i), abs(j))  # Higher score for center proximity

        return score
    
    @staticmethod
    def evaluate_board_state_advanced(board, ai_agent):  # heuristic function 2
        """
        board: game board
        returns: -> high if there's a player2 stone, beside it agent stone,
                    under the agent's stone there's another agent's stone,
                    like that    1 2
                                2
                    suppose ai agent's stone is 2 and human is 1
                    -> low if not
                                               Cases to handle:
                    1) 1 2 2
                         2
                    _______
                    2)    2
                       2
                     1    2
                    _______
                    3) 1
                       2 2
                       2
                    _______
                    4) 1
                       1 1
                       2
                    _______
                    5) 1   1
                         1
                       2
                    _______
                    6)  1
                      2 1 1
        """
        opponent = 3 - ai_agent
        score = 0
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                try:
                    # Case 1
                    if (cell == opponent and row[j + 1] == ai_agent
                            and row[j + 2] == ai_agent and not row[j + 3]
                            and board[i + 1][j + 1] == ai_agent):
                        score += 100  # High priority

                    # Case 2
                    if (cell == ai_agent and board[i - 1][j + 1] == ai_agent
                            and board[i + 1][j + 1] == ai_agent
                            and i - 2 >= 0 and not board[i - 2][j + 2]
                            and board[i + 1][j - 1] == opponent):
                        score += 100  # High priority

                    # Case 3
                    if (cell == ai_agent and row[j + 1] == ai_agent
                            and board[i + 1][j] == ai_agent
                            and j - 1 >= 0 and row[j - 1] == opponent
                            and not board[i][j + 2]):
                        score += 100  # High priority

                    # Case 4 - Vertical stack (New Case)
                    if (i + 2 < len(board) and cell == ai_agent
                            and board[i + 1][j] == opponent
                            and board[i - 1][j] == ai_agent
                            and row[j + 1] == ai_agent
                            and (i + 3 >= len(board) or not board[i + 3][j])):
                        score += 100  # High priority

                    # Case 5
                    if (cell == ai_agent and board[i - 1][j + 1] == ai_agent
                            and board[i - 1][j - 1] == ai_agent
                            and i - 2 >= 0 and not board[i - 2][j + 2]
                            and board[i + 1][j - 1] == opponent):
                        score += 100  # High priority

                    # Case 6
                    if (cell == opponent and row[j - 1] == ai_agent
                            and row[j + 2] == ai_agent and not row[j + 3]
                            and board[i + 1][j + 1] == ai_agent):
                        score += 100  # High priority

                except IndexError:
                    continue

        return score


    def get_best_move(self, max_depth=3, time_limit=2):  # Add a time limit
        best_move = None

        start_time = time.time()  # Start the timer

        print("Evaluating best move...")

        valid_moves = self.get_prioritized_moves()

        for depth in range(1, max_depth + 1):
            current_best_move = None
            current_best_score = float('-inf')

            for row, col in valid_moves:
                if time.time() - start_time > time_limit:
                    return best_move if best_move else current_best_move

                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.player_number
                    score = self.minimax(depth - 1, False, float('-inf'), float('inf'))
                    self.game.board[row][col] = 0

                    if score > current_best_score:
                        current_best_score = score
                        current_best_move = (row, col)

            if current_best_move:
                best_move = current_best_move
        return best_move

    def get_prioritized_moves(self):
        """
        Get list of valid moves, prioritizing strategic positions
        """
        board_size = self.game.board_size
        center = board_size // 2
        moves = []

        # Check center and surrounding positions first
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= center + i < board_size and 0 <= center + j < board_size:
                    moves.append((center + i, center + j))

        # Add positions near existing stones
        for row in range(board_size):
            for col in range(board_size):
                if self.game.board[row][col] != 0:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if (0 <= row + i < board_size and
                                    0 <= col + j < board_size and
                                    (row + i, col + j) not in moves):
                                moves.append((row + i, col + j))

        # Add remaining positions
        for row in range(board_size):
            for col in range(board_size):
                if (row, col) not in moves:
                    moves.append((row, col))

        return moves

    def minimax(self, depth, is_maximizing, alpha, beta):
        """
        Enhanced minimax algorithm with alpha-beta pruning
        """
        winner = self.game.check_win()
        if winner == self.player_number:
            return 10000
        elif winner == self.opponent:
            return -10000
        elif depth == 0:
            return self.evaluate_board_state(self.game.board, self.player_number)

        valid_moves = self.get_prioritized_moves()

        if is_maximizing:
            best_score = float('-inf')
            for row, col in valid_moves:
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.player_number
                    score = self.minimax(depth - 1, False, alpha, beta)
                    self.game.board[row][col] = 0
                    best_score = max(best_score, score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        else:
            best_score = float('inf')
            for row, col in valid_moves:
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.opponent
                    score = self.minimax(depth - 1, True, alpha, beta)
                    self.game.board[row][col] = 0
                    best_score = min(best_score, score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
        return best_score
