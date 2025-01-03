import time

agent = 1
player = 2

agent_patterns = {
    (agent, agent, agent, agent, agent): 1000,  # Win
    (0, agent, agent, agent, agent, 0): 900,  # Open four
    (agent, agent, agent, agent, 0): 800,  # Four
    (0, agent, agent, agent, 0): 200,  # Open three
    (agent, agent, agent, 0, 0): 50,  # Three
    (0, agent, agent, 0): 10,  # Open two
    (agent, agent, 0, 0): 5  # Two
}

player_patterns = {
    (agent,player, player, player, player, agent): 9,
    (player, player, player, player, agent): 900,
    (0, player, player, player, agent, 0): 850,
    (player, player, player, agent, 0): 45,
    (agent, player, player, agent): 250,
    (player,agent,player):150,
    (player,0,player,agent,player):250,
    (player,player,player,agent,player):250,
    (player,player,agent,player,player):250

}

directions = [
    (0, 1), (1, 0), (1, 1), (-1, 1),
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

        self.board[row][col] = self.current_player

        captures = self.check_captures(row, col)
        if captures > 0:
            if self.current_player == 1:
                self.captures_p1 += captures
            elif self.current_player == 2:
                self.captures_p2 += captures

        self.toggle_player()

        print(f"Current player after move: {self.current_player}")  # Debugging line
        return True

    def toggle_player(self):
        #Switch the current player between 1 and 2.
        self.current_player = 3 - self.current_player
        print(f"Current player after toggle: {self.current_player}")  # Debugging line

    def check_captures(self, row, col):
       
        total_captures = 0
        current_stone = self.board[row][col]
        opponent_stone = 3 - current_stone

        for dx, dy in directions:
            total_captures += self.check_direction_captures(row, col, dx, dy, current_stone, opponent_stone)

        return total_captures

    def check_direction_captures(self, row, col, dx, dy, current_stone, opponent_stone):
       
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

        if self.captures_p1 >= 5:
            return 1
        if self.captures_p2 >= 5:
            return 2

        return None  

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
    def evaluate_board_state_advanced(board, player):
        """
        Heuristic function for evaluating board state in a two-player game

        Args:
            board (list): Game board
            player (int): Current player number

        Returns:
            int: Evaluation score of the board state
        """
        opponent = 3 - player  # Toggle between 1 and 2
        score = 0
        board_size = len(board)

        # Directions to check: horizontal, vertical, diagonals
        directions = [
            (0, 1),  # horizontal
            (1, 0),  # vertical
            (1, 1),  # diagonal down-right
            (1, -1)  # diagonal up-right
        ]

        # Check for sequences and potential blocking moves
        for row in range(board_size):
            for col in range(board_size):
                for dx, dy in directions:
                    # Player's sequences
                    player_seq = 0
                    empty_spaces = 0

                    # Check sequence in both directions
                    for step in [1, -1]:
                        for i in range(1, 5):  # Look up to 4 spaces away
                            try:
                                current_pos = board[row + step * i * dx][col + step * i * dy]

                                if current_pos == player:
                                    player_seq += 1
                                elif current_pos == 0:
                                    empty_spaces += 1
                                else:
                                    break
                            except IndexError:
                                break

                    # Scoring for player's sequences
                    if player_seq == 3 and empty_spaces > 0:
                        score += 50  # Potential winning sequence
                    elif player_seq == 4 and empty_spaces > 0:
                        score += 100  # Very close to winning

                    # Opponent blocking logic
                    opp_seq = 0
                    opp_empty_spaces = 0

                    for step in [1, -1]:
                        for i in range(1, 5):
                            try:
                                current_pos = board[row + step * i * dx][col + step * i * dy]

                                if current_pos == opponent:
                                    opp_seq += 1
                                elif current_pos == 0:
                                    opp_empty_spaces += 1
                                else:
                                    break
                            except IndexError:
                                break

                    # Blocking opponent's potential winning sequences
                    if opp_seq == 3 and opp_empty_spaces > 0:
                        score -= 60  # Urgently need to block
                    elif opp_seq == 4 and opp_empty_spaces > 0:
                        score -= 120  # Critical blocking needed

        # Favoring the center of the board (more strategic)
        center = board_size // 2
        score += 10 * (1 if board[center][center] == player else 0)

        return score

    @staticmethod
    def evaluate_board_state_easy(board, player):
        """
        Heuristic function for evaluating board state in a two-player game.

        Args:
            board (list): Game board
            player (int): Current player number

        Returns:
            int: Evaluation score of the board state
        """
        opponent = 3 - player  # Toggle between 1 and 2
        score = 0
        board_size = len(board)

        # Use `analyze_board` to evaluate threats and opportunities
        threats = PenteAI.analyze_board(board, player, opponent, board_size, mode="threats")
        opportunities = PenteAI.analyze_board(board, player, opponent, board_size, mode="opportunities")

        # Add scores for opportunities (player's advantage) with reduced weight
        for _, move_score in opportunities.items():
            score += move_score * 0.7  

        # Subtract scores for threats (opponent's advantage) with increased weight
        for _, move_score in threats.items():
            score -= move_score * 1.3

        # Punish moves near threats
        for _ in threats.keys():
            score -= 20  

        # Favor the center of the board (strategically valuable)
        center = board_size // 2
        if board[center][center] == player:
            score += 10 

        return score

    def get_best_move(self, board, minimax_func, isAlphaBeta, heuristic_fun, max_depth=3, time_limit=2):
        best_move = None
        start_time = time.time()

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

        # Check center and surrounding positions
        for i in range(-2, 3):
            for j in range(-2, 3):
                if 0 <= center + i < board_size and 0 <= center + j < board_size:
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
                prioritized_moves.append((row, col))
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
                    score = self.minimax_without_alpha_Beta(board, depth - 1, False, heuristic_funtion)
                    self.game.board[row][col] = 0
                    best_score = max(best_score, score)
        else:
            best_score = float('inf')
            for row, col in valid_moves:
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.opponent
                    score = self.minimax_without_alpha_Beta(board, depth - 1, True, heuristic_funtion)
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
    
    @staticmethod
    def analyze_board(board, player, opponent, board_size, mode="all"):
        """
        Analyze the board for various threats and opportunities.

        Args:
            board (list): The game board
            player (int): Current player's number
            opponent (int): Opponent's player number
            board_size (int): Size of the game board
            mode (str): The analysis mode ('parallel', 'threats', 'opportunities', 'surrounding', 'cross', 'all')

        Returns:
            list/dict: Depending on the mode, returns a list of moves or a dictionary of scores.
        """
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
        results = []

        if mode in ["all", "opportunities", "threats"]:
            results = {}

        for row in range(board_size):
            for col in range(board_size):
                if board[row][col] == 0:  # Empty spot
                    for dx, dy in directions:
                        opponent_count = 0
                        player_count = 0
                        empty_count = 0
                        surrounding_opponent_count = 0

                        for step in range(-4, 5):  # Look both directions
                            nx, ny = row + step * dx, col + step * dy
                            if 0 <= nx < board_size and 0 <= ny < board_size:
                                if board[nx][ny] == opponent:
                                    opponent_count += 1
                                    if -1 <= step <= 1:
                                        surrounding_opponent_count += 1
                                elif board[nx][ny] == player:
                                    player_count += 1
                                elif board[nx][ny] == 0:
                                    empty_count += 1
                                else:
                                    break

                        # Handle each mode
                        if mode in ["parallel", "all"] and opponent_count >= 2 and empty_count > 0:
                            results.append((row, col))
                            break

                        if mode in ["threats", "all"]:
                            threat_score = opponent_count * 50 if opponent_count >= 2 and empty_count >= 1 else 0
                            opportunity_score = player_count * 40 if player_count >= 2 and empty_count >= 1 else 0
                            total_score = threat_score + opportunity_score
                            if total_score > 0:
                                results[(row, col)] = total_score

                        if mode in ["surrounding", "all"] and surrounding_opponent_count >= 2:
                            results.append((row, col))
                            break

        return results
