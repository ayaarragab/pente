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

    @staticmethod
    def evaluate_board_state(board, player):
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
    import time
    def get_best_move(self, search_depth=2, time_limit=2):  # Add a time limit
        best_score = float('-inf')
        best_move = None

        start_time = time.time()  # Start the timer

        print("Evaluating best move...")

        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                if self.game.is_valid_move(row, col):
                    self.game.board[row][col] = self.player_number

                    score = self.minimax(search_depth - 1, False)

                    self.game.board[row][col] = 0

                    print(f"Evaluating move ({row}, {col}) with score: {score}")

                    if score > best_score:
                        best_score = score
                        best_move = (row, col)

                # Check if the time limit is exceeded
                if time.time() - start_time > time_limit:
                    print("Time limit exceeded, returning best move found so far.")
                    return best_move

        if best_move:
            print(f"Best move found: {best_move} with score: {best_score}")
        else:
            print("No valid move found by AI.")  # Debugging line
        return best_move

    def minimax(self, depth, is_maximizing, alpha=float('-inf'), beta=float('inf')):
        """
        Minimax algorithm with alpha-beta pruning

        Args:
            depth (int): Remaining search depth
            is_maximizing (bool): Whether it's maximizing player's turn
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning

        Returns:
            float: Evaluation score
        """
        # Check win conditions
        winner = self.game.check_win()
        if winner == self.player_number:
            return 1000
        elif winner != 0 and winner != self.player_number:
            return -1000

        # Reached max depth
        if depth == 0:
            return self.evaluate_board_state(self.game.board,self.game.current_player)

        if is_maximizing:
            best_score = float('-inf')
            for row in range(self.game.board_size):
                for col in range(self.game.board_size):
                    if self.game.is_valid_move(row, col):
                        self.game.board[row][col] = self.player_number
                        score = self.minimax(depth - 1, False, alpha, beta)
                        self.game.board[row][col] = 0
                        best_score = max(best_score, score)
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
            return best_score
        else:
            best_score = float('inf')
            opponent = 3 - self.player_number
            for row in range(self.game.board_size):
                for col in range(self.game.board_size):
                    if self.game.is_valid_move(row, col):
                        self.game.board[row][col] = opponent
                        score = self.minimax(depth - 1, True, alpha, beta)
                        self.game.board[row][col] = 0
                        best_score = min(best_score, score)
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
            return best_score


if __name__ == "__main__":
    game = PenteGame()
    print(game.make_move(0, 0))  # Should print True
    print(type(game.current_player), game.current_player)  # Should print <class 'int'> 2
    print(game.make_move(0, 1))  # Should print True
    print(type(game.current_player), game.current_player)  # Should print <class 'int'> 1
    print(game.check_win())  # Should print 0 (no winner yet)
