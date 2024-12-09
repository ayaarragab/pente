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
    def basic_evaluations(board, player):
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
            return score

    @staticmethod
    def evaluate_board_state_advanced(board, player):
        """
        Advanced heuristic function for evaluating Pente board state
        Considers multiple strategic aspects of the game

        Args:
            board (list): Game board
            player (int): Current player number

        Returns:
            int: Comprehensive evaluation score of the board state
        """
        opponent = 3 - player
        board_size = len(board)
        score = 0

        # Directional vectors for checking different board patterns
        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal down-right
            (1, -1)   # Diagonal up-right
        ]

        # Comprehensive pattern scoring with more nuanced evaluations
        patterns = {
            # Winning and critical patterns
            (player, player, player, player, player): 100000,  # Immediate win
            (0, player, player, player, player, 0): 50000,    # Open four (critical threat)
            
            # Strong offensive patterns
            (player, player, player, player, 0): 10000,       # Nearly complete line
            (0, player, player, player, 0): 5000,             # Open three with potential
            (player, player, player, 0, 0): 2000,             # Developing three
            (0, player, player, 0): 500,                      # Open two
            (player, player, 0, 0): 200,                      # Potential two
        }

        # Defensive pattern recognition
        defensive_patterns = {
            (opponent, opponent, opponent, opponent, 0): -40000,  # Block opponent's four
            (0, opponent, opponent, opponent, 0): -20000,         # Block critical threat
            (opponent, opponent, opponent, 0, 0): -5000,          # Block developing line
            (0, opponent, opponent, 0): -1000,                    # Block potential line
        }

        # Capture evaluation with more strategic weighting
        def evaluate_captures(board, player):
            opponent = 3 - player
            capture_score = 0
            capture_locations = []

            for row in range(board_size):
                for col in range(board_size):
                    if board[row][col] == player:
                        for dx, dy in directions:
                            try:
                                # Check for potential captures of exactly two opponent stones
                                if (0 <= row + 3 * dx < board_size and
                                    0 <= col + 3 * dy < board_size and
                                    board[row + dx][col + dy] == opponent and
                                    board[row + 2 * dx][col + 2 * dy] == opponent and
                                    board[row + 3 * dx][col + 3 * dy] == player):
                                    
                                    # Bonus for strategic capture locations
                                    capture_locations.append((row, col))
                                    capture_score += 1000
                            except IndexError:
                                continue
            
            # Additional scoring for multiple captures and strategic capture locations
            if len(capture_locations) > 1:
                capture_score += len(capture_locations) * 500
            
            return capture_score

        # Calculate base score
        score += PenteAI.basic_evaluations(board, player)

        # Evaluate captures
        score += evaluate_captures(board, player)

        # Advanced positional evaluation
        center = board_size // 2
        center_control_bonus = 0
        
        # More sophisticated center control
        for i in range(-3, 4):
            for j in range(-3, 4):
                if 0 <= center + i < board_size and 0 <= center + j < board_size:
                    if board[center + i][center + j] == player:
                        # Exponential decay of bonus based on distance from center
                        center_control_bonus += max(0, 10 - (abs(i) + abs(j))) ** 2

        score += center_control_bonus

        # Mobility and potential move evaluation
        potential_moves = 0
        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == 0:
                    # Check surrounding area for strategic potential
                    surrounding_stones = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if (0 <= row + dx < board_size and 
                                0 <= col + dy < board_size and 
                                board[row + dx][col + dy] != 0):
                                surrounding_stones += 1
                    
                    if surrounding_stones > 0:
                        potential_moves += surrounding_stones * 10

        score += potential_moves

        # Pattern recognition
        for row in range(board_size):
            for col in range(board_size):
                for dx, dy in directions:
                    # Check offensive patterns
                    for pattern, pattern_score in patterns.items():
                        if PenteAI._check_pattern(board, row, col, dx, dy, pattern):
                            score += pattern_score

                    # Check defensive patterns
                    for pattern, pattern_score in defensive_patterns.items():
                        if PenteAI._check_pattern(board, row, col, dx, dy, pattern):
                            score += pattern_score

        return score

    @staticmethod
    def _check_pattern(board, row, col, dx, dy, pattern):
        """
        Helper method to check if a specific pattern exists on the board
        
        Args:
            board (list): Game board
            row (int): Starting row
            col (int): Starting column
            dx (int): Row direction
            dy (int): Column direction
            pattern (tuple): Pattern to match

        Returns:
            bool: Whether the pattern is found
        """
        board_size = len(board)
        pattern_length = len(pattern)

        # Verify pattern fits on board
        if not (0 <= row + (pattern_length - 1) * dx < board_size and
                0 <= col + (pattern_length - 1) * dy < board_size):
            return False

        # Check if pattern matches
        for i, value in enumerate(pattern):
            if board[row + i * dx][col + i * dy] != value:
                return False

        return True

    @staticmethod
    def evaluate_board_state_easy(board, ai_agent):  # heuristic function 2
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
        score = PenteAI.basic_evaluations(board, opponent)
        # Position evaluation
        board_size = len(board)
        center = len(board) // 2
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= center + i < board_size and 0 <= center + j < board_size:
                    if board[center + i][center + j] == opponent:
                        score += 5 - max(abs(i), abs(j))

        return score

    def get_best_move(self, minimax_func, isAlphaBeta, heuristic_fun, max_depth=3, time_limit=2):  # Add a time limit
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
                    if isAlphaBeta:
                        score = minimax_func(depth - 1, False, float('-inf'), float('inf'), heuristic_fun)
                    else:
                        score = minimax_func(depth - 1, False, heuristic_fun)
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

    def minimax_without_alpha_Beta(self, depth, is_maximizing, heuristic_funtion):
        """
        Minimax algorithm without alpha-beta pruning
        """
        winner = self.game.check_win()
        if winner == self.player_number:
            return 10000
        elif winner == self.opponent:
            return -10000
        elif depth == 0:
            return heuristic_funtion(self.game.board, self.player_number)

        valid_moves = self.get_prioritized_moves()

        if is_maximizing:
            best_score = float('-inf')
            for row, col in valid_moves:
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.player_number
                    score = self.minimax(depth - 1, False)
                    self.game.board[row][col] = 0
                    best_score = max(best_score, score)
        else:
            best_score = float('inf')
            for row, col in valid_moves:
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.opponent
                    score = self.minimax(depth - 1, True)
                    self.game.board[row][col] = 0
                    best_score = min(best_score, score)
        return best_score

    def minimax(self, depth, is_maximizing, alpha, beta, heuristic_funtion):
        """
        Enhanced minimax algorithm with alpha-beta pruning
        """
        winner = self.game.check_win()
        if winner == self.player_number:
            return 10000
        elif winner == self.opponent:
            return -10000
        elif depth == 0:
            return heuristic_funtion(self.game.board, self.player_number)

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
