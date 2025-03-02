DIRECTIONS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

class Board:
    def __init__(self):
        self.size = 8
        self.grid = self._initialize_board()
        self.bases = [((1, 2), 0), ((1, 3), 0), ((1, 4), 0), ((1, 5), 0),
                      ((6, 2), 1), ((6, 3), 1), ((6, 4), 1), ((6, 5), 1)]

    def _initialize_board(self):
        """Creates an empty board."""
        board = {}
        for row in range(self.size):
            for col in range(self.size):
                board[(row, col)] = None
        return board

    def place_pod(self, position, player, prongs=None):
        """Places a pod at a given position."""
        if prongs is None:
            prongs = []
        self.grid[position] = {"player": player, "prongs": prongs}

    def move_pod(self, start_pos, end_pos):
        """Handles pod movement, jumping, and capturing."""
        if start_pos not in self.grid or self.grid[start_pos] is None:
            raise ValueError("No pod at the starting position!")

        pod = self.grid[start_pos]
        player = pod["player"]

        direction = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])

        # Determine if the move follows a valid prong direction
        valid_prong = None
        for prong_dir, vector in DIRECTIONS.items():
            if vector == direction and prong_dir in pod["prongs"]:
                valid_prong = prong_dir
                break

        # Check for jump (two-step move)
        is_jump = (
                not valid_prong and
                (direction[0] % 2 == 0 and direction[1] % 2 == 0)  # Must be two-step move
        )

        if not valid_prong and not is_jump:
            raise ValueError("Invalid move: No prong in that direction!")

        if is_jump:
            # Compute the midpoint
            mid_pos = ((start_pos[0] + end_pos[0]) // 2, (start_pos[1] + end_pos[1]) // 2)

            if mid_pos not in self.grid or self.grid[mid_pos] is None:
                raise ValueError("Invalid jump: No pod to jump over!")

            if self.grid[end_pos] is not None:
                raise ValueError("Invalid move: Target position occupied!")

        elif self.grid[end_pos] is not None:
            # Capture case: Enemy pod is at end position
            if self.grid[end_pos]["player"] == player:
                raise ValueError("Invalid move: Cannot capture your own pod!")

            # Remove a prong from the opponent's pod
            if self.grid[end_pos]["prongs"]:
                self.grid[end_pos]["prongs"].pop()  # Remove a random prong

            # If no prongs remain, remove the pod
            if not self.grid[end_pos]["prongs"]:
                self.grid[end_pos] = None

        # Move the pod
        self.grid[end_pos] = pod
        self.grid[start_pos] = None

    def add_prong(self, position, direction):
        """Adds a prong to a pod if allowed."""
        if position not in self.grid or self.grid[position] is None:
            raise ValueError("No pod at the given position!")

        if direction not in DIRECTIONS:
            raise ValueError("Invalid prong direction!")

        self.grid[position]["prongs"].append(direction)

    def __repr__(self):
        """Displays the board."""
        display = []
        for row in range(self.size):
            row_display = []
            for col in range(self.size):
                cell = self.grid[(row, col)]
                if cell:
                    row_display.append("P")  # Pod present
                else:
                    row_display.append(".")  # Empty
            display.append(" ".join(row_display))
        return "\n".join(display)
