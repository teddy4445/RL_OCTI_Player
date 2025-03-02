import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class OctiNet(nn.Module):
    def __init__(self):
        super(OctiNet, self).__init__()
        self.fc1 = nn.Linear(64, 128)  # 64 input features (board state)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)  # Output: board evaluation score

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)  # Single score
