import pygame
import sys
import time

# Constants
from board import DIRECTIONS

GRID_SIZE = 8
CELL_SIZE = 80
BOARD_COLOR = (200, 200, 200)
PLAYER1_COLOR = (50, 50, 200)  # Blue
PLAYER2_COLOR = (200, 50, 50)  # Red
PLAYER1_BASE_COLOR = (150, 150, 255)  # Light blue
PLAYER2_BASE_COLOR = (255, 150, 150)  # Light red
PRONG_COLOR = (255, 255, 0)  # Yellow
TEXT_COLOR = (0, 0, 0)
HISTORY_BG_COLOR = (240, 240, 240)
ANIMATION_SPEED = 0.3  # Animation duration in seconds

PANEL_WIDTH = 200
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE + PANEL_WIDTH
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE


class OctiGameGUI:
    def __init__(self, game):
        pygame.init()
        self.game = game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Octi Game")
        self.selected_pod = None
        self.prong_options = []  # Stores possible prong addition positions
        self.font = pygame.font.Font(None, 30)

    def draw_board(self):
        """Draws the game board and base locations."""
        self.screen.fill(BOARD_COLOR)

        # Highlight bases
        for (row, col), base_owner in self.game.board.bases:
            base_color = PLAYER1_BASE_COLOR if base_owner == 0 else PLAYER2_BASE_COLOR
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, base_color, rect)

        # Draw grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)

    def draw_pods(self):
        """Draws pods and their prongs, highlighting the selected pod."""
        for (row, col), pod in self.game.board.grid.items():
            if pod:
                base_color = PLAYER1_COLOR if pod["player"].index == 0 else PLAYER2_COLOR
                color = tuple(max(0, c - 50) for c in base_color) if (row, col) == self.selected_pod else base_color

                pygame.draw.circle(
                    self.screen, color,
                    ((col * CELL_SIZE) + CELL_SIZE // 2, (row * CELL_SIZE) + CELL_SIZE // 2), 20
                )

                # Highlight current player's pods with a white border
                if pod["player"].index == self.game.current_player_index:
                    pygame.draw.circle(
                        self.screen, (255, 255, 255),
                        ((col * CELL_SIZE) + CELL_SIZE // 2, (row * CELL_SIZE) + CELL_SIZE // 2), 22, 2
                    )

                if "prongs" in pod and pod["prongs"]:  # Draw prongs
                    for prong in pod["prongs"]:
                        self.draw_prong(row, col, prong)

    def draw_prong(self, row, col, direction):
        """Draws a prong from the given position."""
        center_x = col * CELL_SIZE + CELL_SIZE // 2
        center_y = row * CELL_SIZE + CELL_SIZE // 2

        if direction in DIRECTIONS:
            offset_x, offset_y = DIRECTIONS[direction][0] * 20, DIRECTIONS[direction][1] * 20
            pygame.draw.line(self.screen, PRONG_COLOR, (center_x, center_y),
                             (center_x + offset_x, center_y + offset_y), 3)

    def draw_prong_options(self):
        """Draws yellow boxes at positions where a prong can be added."""
        for row, col in self.prong_options:
            rect = pygame.Rect(col * CELL_SIZE + 25, row * CELL_SIZE + 25, 30, 30)
            pygame.draw.rect(self.screen, PRONG_COLOR, rect)

    def get_prong_positions(self, pod_position):
        """Returns valid prong addition positions."""
        row, col = pod_position
        pod = self.game.board.grid.get((row, col))
        if not pod or "prongs" not in pod:
            return []

        existing_prongs = set(pod["prongs"])
        possible_positions = []

        for direction, (dr, dc) in DIRECTIONS.items():
            if direction not in existing_prongs:  # Avoid duplicate prongs
                possible_positions.append((row + dr, col + dc))

        return possible_positions

    def get_cell_from_mouse(self, pos):
        """Returns the board position from a mouse click."""
        x, y = pos
        return y // CELL_SIZE, x // CELL_SIZE

    def draw_text(self, text, position, color=TEXT_COLOR):
        """Displays text on the screen."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def get_valid_moves(self, pod_position, allow_multi_jump=False, visited=None):
        """Returns valid move positions, including multi-jumps."""
        row, col = pod_position
        valid_moves = []

        if visited is None:
            visited = set()

        for direction in DIRECTIONS.values():
            dr, dc = direction
            adjacent_pos = (row + dr, col + dc)
            jump_pos = (row + 2 * dr, col + 2 * dc)

            # Normal move (only allowed if it's the first move)
            if not allow_multi_jump and adjacent_pos not in self.game.board.grid:
                valid_moves.append(adjacent_pos)

            # Jumping: If adjacent cell has a pod and the jump cell is empty
            elif adjacent_pos in self.game.board.grid and jump_pos not in self.game.board.grid:
                if jump_pos not in visited:  # Avoid infinite loops
                    valid_moves.append(jump_pos)
                    visited.add(jump_pos)

                    # Recursively check for more jumps
                    valid_moves.extend(self.get_valid_moves(jump_pos, allow_multi_jump=True, visited=visited))

        return valid_moves

    def draw_possible_moves(self, pod_position):
        """Highlights possible move locations for the selected pod."""
        valid_moves = self.get_valid_moves(pod_position)

        for row, col in valid_moves:
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, (0, 255, 0), rect, 5)  # Green border for valid moves

    def move_pod_animated(self, start, end):
        """Animates a pod moving from `start` to `end`."""
        x1, y1 = start[1] * CELL_SIZE + CELL_SIZE // 2, start[0] * CELL_SIZE + CELL_SIZE // 2
        x2, y2 = end[1] * CELL_SIZE + CELL_SIZE // 2, end[0] * CELL_SIZE + CELL_SIZE // 2
        start_time = time.time()

        while time.time() - start_time < ANIMATION_SPEED:
            progress = (time.time() - start_time) / ANIMATION_SPEED
            x = int(x1 + progress * (x2 - x1))
            y = int(y1 + progress * (y2 - y1))

            self.draw_board()
            self.draw_pods()
            pygame.draw.circle(self.screen, PLAYER1_COLOR if self.game.current_player_index == 0 else PLAYER2_COLOR,
                               (x, y), 20)
            self.draw_history_panel()
            pygame.display.flip()

        self.draw_board()
        self.draw_pods()
        self.draw_history_panel()
        pygame.display.flip()

    def draw_history_panel(self):
        """Draws the move history panel on the right side of the screen."""
        history_rect = pygame.Rect(GRID_SIZE * CELL_SIZE, 0, PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, HISTORY_BG_COLOR, history_rect)

        # Title
        self.draw_text("Move History", (GRID_SIZE * CELL_SIZE + 20, 10), (0, 0, 0))

        # Display last 10 moves
        recent_moves = self.game.move_log[-10:]
        for i, move in enumerate(reversed(recent_moves)):
            self.draw_text(move[1], (GRID_SIZE * CELL_SIZE + 10, 40 + i * 30))

    def run(self):
        """Runs the main game loop."""
        running = True
        while running:
            self.draw_board()
            self.draw_pods()
            self.draw_history_panel()

            if self.selected_pod:
                self.draw_possible_moves(self.selected_pod)
                self.draw_prong_options()

            if self.game.winner:
                self.draw_text(f"{self.game.winner} Wins!", (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game.winner:
                    row, col = self.get_cell_from_mouse(event.pos)

                    if event.button == 1:  # Left-click
                        if (row, col) in self.prong_options:
                            # Add prong as a move
                            direction = next((d for d, (dr, dc) in DIRECTIONS.items() if (row, col) == (self.selected_pod[0] + dr, self.selected_pod[1] + dc)), None)
                            if direction:
                                self.game.play_turn(f"prong {str(self.selected_pod).replace(' ', '')} {direction}")
                                self.selected_pod = None
                                self.prong_options = []
                                continue

                        if self.selected_pod:
                            old_position = self.selected_pod
                            new_position = (row, col)

                            valid_moves = self.get_valid_moves(old_position, allow_multi_jump=True)

                            if new_position in valid_moves:
                                self.move_pod_animated(old_position, new_position)
                                self.game.play_turn(f"move {str(old_position).replace(' ', '')} to {new_position}")
                                self.selected_pod = None
                                self.prong_options = []

                            elif new_position == old_position:
                                self.prong_options = self.get_prong_positions(new_position)

                        elif (row, col) in self.game.board.grid and self.game.board.grid[(row, col)] is not None and self.game.board.grid[(row, col)]["player"].index == self.game.current_player_index:
                            self.selected_pod = (row, col)
                            self.prong_options = self.get_prong_positions((row, col))

        pygame.quit()
        sys.exit()
