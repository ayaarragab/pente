import unittest
from pente import PenteGame

class TestPenteGame(unittest.TestCase):
    def setUp(self):
        self.game = PenteGame()

    def test_is_valid_move(self):
        self.assertTrue(self.game.is_valid_move(0, 0))
        self.assertFalse(self.game.is_valid_move(-1, 0))
        self.assertFalse(self.game.is_valid_move(0, 19))
        self.game.board[0][0] = 1
        self.assertFalse(self.game.is_valid_move(0, 0))

    def test_make_move(self):
        self.assertTrue(self.game.make_move(0, 0))
        self.assertEqual(self.game.board[0][0], 1)
        self.assertFalse(self.game.make_move(0, 0))  # Move to the same spot

    def test_check_win(self):
        self.game.board[0] = [1, 1, 1, 1, 1]  # Horizontal win
        self.assertEqual(self.game.check_win(), 1)

if __name__ == '__main__':
    unittest.main()