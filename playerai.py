import torch


class OctiAIPlayer:
    def __init__(self, name, model, depth=3):
        self.name = name
        self.model = model
        self.depth = depth

    def choose_move(self, game):
        """Chooses the best move using Minimax + Alpha-Beta + RL evaluation."""
        _, best_move = self.minimax(game, self.depth, float("-inf"), float("inf"), True)
        return best_move

    def minimax(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or game.winner:
            return self.evaluate_board(game), None

        possible_moves = game.get_possible_moves()
        if not possible_moves:
            return self.evaluate_board(game), None

        best_move = None
        if maximizing_player:
            max_eval = float("-inf")
            for move in possible_moves:
                game.make_temporary_move(move)
                eval_score, _ = self.minimax(game, depth - 1, alpha, beta, False)
                game.undo_temporary_move(move)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval, best_move
        else:
            min_eval = float("inf")
            for move in possible_moves:
                game.make_temporary_move(move)
                eval_score, _ = self.minimax(game, depth - 1, alpha, beta, True)
                game.undo_temporary_move(move)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def evaluate_board(self, game):
        """Uses RL model to evaluate board state."""
        board_state = game.board.to_vector()  # Convert board to numeric format
        with torch.no_grad():
            score = self.model(torch.tensor(board_state, dtype=torch.float32))
        return score.item()
