import time
from pente import PenteGame, PenteAI

def performance_test():
    game = PenteGame()
    ai = PenteAI(game, player_number=2)

    depths = [1, 2, 3, 4, 5]
    for depth in depths:
        start_time = time.time()
        ai.get_best_move(
            board=game.board,
            minimax_func=ai.minimax_without_alpha_Beta,
            isAlphaBeta=False,
            heuristic_fun=ai.evaluate_board_state_easy,
            max_depth=depth,
            time_limit=2  # Example time limit in seconds
        )
        without_ab_time = time.time() - start_time

        start_time = time.time()
        ai.get_best_move(
            board=game.board,
            minimax_func=ai.minimax,
            isAlphaBeta=True,
            heuristic_fun=ai.evaluate_board_state_easy,
            max_depth=depth,
            time_limit=2  # Example time limit in seconds
        )
        with_ab_time = time.time() - start_time

        print(f"Depth: {depth}, Without Alpha-Beta: {without_ab_time:.4f}s, With Alpha-Beta: {with_ab_time:.4f}s")

if __name__ == '__main__':
    performance_test()