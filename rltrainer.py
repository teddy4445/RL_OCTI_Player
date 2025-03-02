import torch

from octigame import OctiGame
from octinet import OctiNet
from playerai import OctiAIPlayer

class RLTrainer:
    def __init__(self, model, learning_rate=0.001):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.loss_fn = torch.nn.MSELoss()

    def train_step(self, board_state, target):
        self.optimizer.zero_grad()
        prediction = self.model(torch.tensor(board_state, dtype=torch.float32))
        loss = self.loss_fn(prediction, torch.tensor(target, dtype=torch.float32))
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def train_from_games(self, game_history):
        """Train AI from past self-play games."""
        for board_state, outcome in game_history:
            target = outcome  # Target is game result (+1 win, -1 loss, 0 draw)
            self.train_step(board_state, target)
