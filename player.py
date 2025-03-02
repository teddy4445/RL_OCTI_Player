class Player:
    def __init__(self, index: int, is_ai: bool = False):
        self.index = index
        self.is_ai = is_ai

    def __repr__(self):
        return f"Player({self.index}, AI={self.is_ai})"
