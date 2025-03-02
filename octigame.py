from board import Board
from player import Player


class OctiGame:
    def __init__(self, player1: Player, player2: Player, initial_position=None, max_moves=100):
        self.players = [player1, player2]
        self.current_player_index = 0
        self.board = initial_position if initial_position else Board()
        self.winner = None  # Track the winner
        self.move_log = []  # Store move history
        self.max_moves = max_moves  # Draw condition
        self._setup_pods()

    def _setup_pods(self):
        """Initial placement of pods."""
        for col in range(4):
            self.board.place_pod((1, 2+col), self.players[0], {})  # Player 1
            self.board.place_pod((6, 2+col), self.players[1], {})  # Player 2

    def switch_turn(self):
        """Switch turn unless the game is over."""
        if self.winner is None:
            self.current_player_index = 1 - self.current_player_index

    def play_turn(self, move):
        """Processes a player's move, logs it, and checks for game end conditions."""
        if self.winner:
            print(f"Game over! {self.winner} already won.")
            return

        player = self.get_current_player()
        self.move_log.append((player.index, move))  # Log move

        if move.startswith("move"):
            _, start, _, end = move.split()
            start = tuple(map(int, start.strip("()").split(",")))
            end = tuple(map(int, end.strip("()").split(",")))
            self.board.move_pod(start, end)

            # Check for victory (reaching home row or eliminating opponent)
            self.check_victory(player, end)

        elif move.startswith("prong"):
            _, position, direction = move.split()
            position = tuple(map(int, position.strip("()").split(",")))
            self.board.add_prong(position, direction)

        else:
            print("Invalid move, please try again...")
            return False

        print(self)
        self.check_draw()  # Check if game should end in a draw
        self.switch_turn()

    def get_possible_moves(self):
        """Generates all legal moves for the current player efficiently."""
        moves = []
        player_name = self.players[self.current_player_index].name
        player_pods = self.board.get_pods(player_name)

        for pod in player_pods:
            for move in self.get_legal_moves_for_pod(pod):
                moves.append(move)

        return moves

    def get_legal_moves_for_pod(self, pod):
        """Generates legal moves for a given pod based on current state."""
        legal_moves = []
        row, col, arrows = pod.position, pod.arrows

        # Step 1: Add basic move directions (only if arrows exist)
        move_directions = self.get_possible_directions(arrows)
        for direction in move_directions:
            new_pos = (row + direction[0], col + direction[1])
            if self.board.is_valid_move(row, col, new_pos):
                legal_moves.append((row, col, new_pos))

        # Step 2: Capture moves (jump over opponent)
        for direction in move_directions:
            jump_pos = (row + 2 * direction[0], col + 2 * direction[1])
            if self.board.is_valid_capture(row, col, jump_pos):
                legal_moves.append(("capture", row, col, jump_pos))

        return legal_moves

    def get_possible_directions(self, arrows):
        """Returns possible move directions based on active arrows."""
        directions = []
        if "N" in arrows:
            directions.append((-1, 0))
        if "S" in arrows:
            directions.append((1, 0))
        if "E" in arrows:
            directions.append((0, 1))
        if "W" in arrows:
            directions.append((0, -1))
        return directions

    def check_victory(self, player, end_pos):
        """Checks if a player has won by reaching home row or eliminating all opponent's pods."""
        opponent = self.players[1 - self.players.index(player)]

        # Check if the player reached the opponent's home row
        if (player == self.players[0] and end_pos[0] == 7) or (player == self.players[1] and end_pos[0] == 0):
            self.winner = player
            print(f"🏆 {player.name} WINS by reaching home row!")
            return

        # Check if the opponent has any pods left
        opponent_has_pods = any(
            pod and pod["player"] == opponent for pod in self.board.grid.values()
        )

        if not opponent_has_pods:
            self.winner = player
            print(f"🏆 {player.name} WINS by eliminating all opponent pods!")

    def check_draw(self):
        """Checks for a draw condition."""
        if len(self.move_log) >= self.max_moves:
            self.winner = "DRAW"
            print("🤝 Game ends in a DRAW due to move limit.")
            return

        # Check if both players have no valid moves left
        if not self.has_valid_moves(self.players[0]) and not self.has_valid_moves(self.players[1]):
            self.winner = "DRAW"
            print("🤝 Game ends in a DRAW (no valid moves left).")

    def has_valid_moves(self, player):
        """Returns True if the player has any valid moves left."""
        for position, pod in self.board.grid.items():
            if pod and pod["player"] == player:
                # Check if at least one move is possible
                for direction in pod["prongs"]:
                    new_pos = self.board.get_new_position(position, direction)
                    if new_pos and self.board.is_valid_position(new_pos):
                        return True
        return False

    def get_current_player(self):
        """Returns the current player."""
        return self.players[self.current_player_index]

    def get_move_log(self):
        """Returns a list of all moves played."""
        return self.move_log

    def __repr__(self):
        board_state = f"{self.players[0]} vs {self.players[1]}\nCurrent turn: {self.get_current_player().name}\n{self.board}"
        if self.winner:
            board_state += f"\n🏆 {self.winner if self.winner != 'DRAW' else '🤝 DRAW'}"
        return board_state
