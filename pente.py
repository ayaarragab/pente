import time

agent = 1
player = 2

agent_patterns = {
    (agent, agent, agent, agent, agent): 10000,  # Win
    (0, agent, agent, agent, agent, 0): 2000,  # Open four
    (agent, agent, agent, agent, 0): 800,  # Four
    (0, agent, agent, agent, 0): 200,  # Open three
    (agent, agent, agent, 0, 0): 50,  # Three
    (0, agent, agent, 0): 10,  # Open two
    (agent, agent, 0, 0): 5  # Two
}

player_patterns = {
    (player, player, player, player, 0): -900,  # Block player's four
    (0, player, player, player, 0): -300,  # Block player's open three
    (player, player, player, 0, 0): -80,  # Block player's three
    (0, player, player, 0): -20  # Block player's open two
}

directions = [
    (0, 1), (1, 0), (1, 1), (-1, 1),  # horizontal, vertical, diagonals
    (0, -1), (-1, 0), (-1, -1), (1, -1)
]

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

    def get_best_move(self, board, minimax_func, isAlphaBeta, heuristic_fun, max_depth=3, time_limit=2):  # Add a time limit
        best_move = None

        start_time = time.time()  # Start the timer

        print("Evaluating best move...")

        valid_moves = self.get_prioritized_moves(board)

        for depth in range(1, max_depth + 1):
            current_best_move = None
            current_best_score = float('-inf')

            for row, col in valid_moves:
                if time.time() - start_time > time_limit:
                    return best_move if best_move else current_best_move

                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.player_number
                    if isAlphaBeta:
                        score = minimax_func(board, depth - 1, False, float('-inf'), float('inf'), heuristic_fun)
                    else:
                        score = minimax_func(board, depth - 1, False, heuristic_fun)
                    self.game.board[row][col] = 0

                    if score > current_best_score:
                        current_best_score = score
                        current_best_move = (row, col)
                    print(current_best_score)
            if current_best_move:
                best_move = current_best_move
        return best_move

    def get_prioritized_moves(self, board):
        """
        Get list of valid moves, prioritizing strategic positions
        """
        board_size = self.game.board_size
        prioritized_moves = []
        center = board_size // 2
        important_agent_pattern = [(0, 1, 1, 1, 1, 0), 
                                   (2, 1, 1, 1, 1, 0), 
                                   (0, 1, 1, 1, 1, 2)]
        for row in range(board_size):
            for col in range(board_size):        
                if self.game.is_valid_move(row, col):
                    for dx, dy in directions:
                        for pattern in important_agent_pattern:
                            # Actually check if the pattern matches
                            pattern_matches = all(
                                0 <= row + i * dx < board_size and 
                                0 <= col + i * dy < board_size and
                                board[row + i * dx][col + i * dy] == cell
                                for i, cell in enumerate(pattern)
                            )
                            
                            if pattern_matches and (row, col) not in prioritized_moves:
                                prioritized_moves.append((row, col))
                                break
        # Check for captures (higher priority)
        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == player:
                    for dx, dy in directions:
                        try:
                            if (0 <= row + 4 * dx < board_size and
                                    0 <= col + 4 * dy < board_size and
                                    board[row + dx][col + dy] == agent and
                                    board[row + 2 * dx][col + 2 * dy] == player and
                                    board[row + 3 * dx][col + 3 * dy] == player
                                    and self.game.is_valid_move(row + 4 * dx, col + 4 * dy)):
                                if (row + 4 * dx, col + 4 * dy) not in prioritized_moves:
                                    prioritized_moves.append((row + 4 * dx, col + 4 * dy))
                        except IndexError:
                            continue
        # Check player (opponent) patterns
        for row in range(board_size):
            for col in range(board_size):
                if self.game.is_valid_move(row, col):
                    for dx, dy in directions:
                        for pattern, _ in player_patterns.items():
                            pattern_found = True
                            pattern_length = len(pattern)

                            if not (0 <= row + (pattern_length - 1) * dx < board_size and
                                    0 <= col + (pattern_length - 1) * dy < board_size):
                                continue

                            for i, value in enumerate(pattern):
                                if board[row + i * dx][col + i * dy] != value:
                                    pattern_found = False
                                    break

                            if pattern_found and (row, col - 1) not in prioritized_moves:
                                prioritized_moves.append((row, col - 1))

        # Check center and surrounding positions
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= center + i < board_size and 0 <= center + j < board_size:
                    if (center + i, center + j) not in prioritized_moves:
                        prioritized_moves.append((center + i, center + j))

        # Add positions near existing stones
        for row in range(board_size):
            for col in range(board_size):
                if self.game.board[row][col] != 0:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if (0 <= row + i < board_size and
                                    0 <= col + j < board_size and
                                    (row + i, col + j) not in prioritized_moves):
                                prioritized_moves.append((row + i, col + j))

        # Add remaining positions
        for row in range(board_size):
            for col in range(board_size):
                if (row, col) not in prioritized_moves:
                    prioritized_moves.append((row, col))
        return prioritized_moves


        # Check center and surrounding positions
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= center + i < board_size and 0 <= center + j < board_size:
                    prioritized_moves.add((center + i, center + j))

        # Add positions near existing stones
        for row in range(board_size):
            for col in range(board_size):
                if self.game.board[row][col] != 0:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if (0 <= row + i < board_size and
                                    0 <= col + j < board_size and
                                    (row + i, col + j) not in prioritized_moves):
                                prioritized_moves.add((row + i, col + j))

        # Add remaining positions
        for row in range(board_size):
            for col in range(board_size):
                prioritized_moves.add((row, col))
        return prioritized_moves

    def minimax_without_alpha_Beta(self, board, depth, is_maximizing, heuristic_funtion):
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

        valid_moves = self.get_prioritized_moves(board)

        if is_maximizing:
            best_score = float('-inf')
            for row, col in valid_moves:
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.player_number
                    score = self.minimax_without_alpha_Beta(depth - 1, False, heuristic_funtion)
                    self.game.board[row][col] = 0
                    best_score = max(best_score, score)
        else:
            best_score = float('inf')
            for row, col in valid_moves:
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.opponent
                    score = self.minimax_without_alpha_Beta(depth - 1, True, heuristic_funtion)
                    self.game.board[row][col] = 0
                    best_score = min(best_score, score)
        return best_score

    def minimax(self, board, depth, is_maximizing, alpha, beta, heuristic_funtion=None):
        """
        Enhanced minimax algorithm with alpha-beta pruning
        """
        if not heuristic_funtion:
            heuristic_funtion = PenteAI.evaluate_board_state_easy
        winner = self.game.check_win()
        if winner == self.player_number:
            return 10000
        elif winner == self.opponent:
            return -10000
        elif depth == 0:
            return heuristic_funtion(self.game.board, self.player_number)

        valid_moves = self.get_prioritized_moves(board)

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
                    score = self.minimax(board, depth - 1, True, alpha, beta)
                    self.game.board[row][col] = 0
                    best_score = min(best_score, score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
        return best_score
