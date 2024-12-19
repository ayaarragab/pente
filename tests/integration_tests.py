import unittest
from pente import PenteGame, PenteAI

class TestPenteIntegration(unittest.TestCase):
    def setUp(self):
        self.game = PenteGame()
        self.ai = PenteAI(self.game, player_number=2)

    def test_ai_move(self):
        self.game.make_move(0, 0)  # Player 1 move
        ai_move = self.ai.get_best_move(
            board=self.game.board,
            minimax_func=self.ai.minimax,
            isAlphaBeta=True,
            heuristic_fun=self.ai.evaluate_board_state_easy,
            max_depth=3,  # Example depth
            time_limit=2  # Example time limit in seconds
        )
        self.assertTrue(self.game.is_valid_move(ai_move[0], ai_move[1]))
        self.game.make_move(ai_move[0], ai_move[1])
        self.assertEqual(self.game.board[ai_move[0]][ai_move[1]], 2)

if __name__ == '__main__':
    unittest.main()