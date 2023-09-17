from a2_support import *
from typing import List, Tuple, Dict


# Write your classes here


class Tile:
    def __init__(self):
        pass

    def is_blocking(self) -> bool:
        return False

    def get_type(self) -> str:
        return "Abstract Tile"

    def __str__(self) -> str:
        return self.get_type()

    def __repr__(self) -> str:
        return self.__str__()


class Floor(Tile):
    def get_type(self) -> str:
        return FLOOR


class Wall(Tile):
    def is_blocking(self) -> bool:
        return True

    def get_type(self) -> str:
        return WALL


class Goal(Tile):
    def __init__(self):
        super().__init__()
        self.filled = False

    def is_filled(self) -> bool:
        return self.filled

    def fill(self) -> None:
        self.filled = True

    def get_type(self) -> str:
        if self.filled:
            return FILLED_GOAL
        return GOAL

    def __str__(self) -> str:
        return self.get_type()

    def __repr__(self) -> str:
        return self.get_type()


class Entity:
    def get_type(self) -> str:
        return "Abstract Entity"

    def is_movable(self) -> bool:
        return False

    def __str__(self) -> str:
        return self.get_type()

    def __repr__(self) -> str:
        return self.__str__()


class Crate(Entity):
    def __init__(self, strength: int) -> None:
        super().__init__()
        self.strength = strength

    def get_type(self) -> str:
        return CRATE

    def is_movable(self) -> bool:
        return True

    def get_strength(self) -> int:
        return self.strength

    def __str__(self) -> str:
        return str(self.strength)

    def __repr__(self) -> str:
        return str(self.strength)


class Potion(Entity):
    def __init__(self):
        super().__init__()

    def effect(self) -> dict[str, int]:
        return {}

    def get_type(self) -> str:
        return "Potion"

    def __str__(self) -> str:
        return self.get_type()

    def __repr__(self) -> str:
        return self.get_type()


class StrengthPotion(Potion):
    def effect(self) -> dict[str, int]:
        return {"strength": 2}

    def get_type(self) -> str:
        return STRENGTH_POTION


class MovePotion(Potion):
    def effect(self) -> dict[str, int]:
        return {"moves": 5}

    def get_type(self) -> str:
        return MOVE_POTION


class FancyPotion(Potion):
    def effect(self) -> dict[str, int]:
        return {'strength': 2, 'moves': 2}

    def get_type(self) -> str:
        return FANCY_POTION


class Player(Entity):
    def __init__(self, start_strength: int, moves_remaining: int) -> None:
        super().__init__()
        self.strenght = start_strength
        self.moves_remaining = moves_remaining

    def get_strength(self) -> int:
        return self.strenght

    def add_strength(self, amount: int) -> None:
        self.strenght += amount

    def get_moves_remaining(self) -> int:
        return self.moves_remaining

    def add_moves_remaining(self, amount: int) -> None:
        self.moves_remaining += amount

    def apply_effect(self, potion_effect: dict[str, int]) -> None:
        for effect, value in potion_effect.items():
            if effect == "strength":
                self.add_strength(value)
            elif effect == "moves":
                self.add_moves_remaining(value)

    def is_movable(self) -> bool:
        return self.moves_remaining > 0

    def get_type(self) -> str:
        return PLAYER


def convert_maze(game: List[List[str]]) -> Tuple[List[List[Tile]], Dict[Tuple[int, int], Entity], Tuple[int, int]]:
    maze = []
    entities = {}
    player_position = None

    for row_index, row in enumerate(game):
        maze_row = []
        for col_index, cell in enumerate(row):
            if cell == WALL:
                maze_row.append(Wall())
            elif cell == FLOOR:
                maze_row.append(Floor())
            elif cell == GOAL:
                maze_row.append(Goal())
            elif cell.isdigit():
                crate_strength = int(cell)
                maze_row.append(Crate(crate_strength))
                entities[(row_index, col_index)] = Crate(crate_strength)
            elif cell == STRENGTH_POTION:
                maze_row.append(StrengthPotion())
            elif cell == MOVE_POTION:
                maze_row.append(MovePotion())
            elif cell == FANCY_POTION:
                maze_row.append(FancyPotion())
            elif cell == PLAYER:
                player_position = (row_index, col_index)
            else:
                raise ValueError(f"Unknown character '{cell}' in the maze")

        maze.append(maze_row)

    return maze, entities, player_position


class SokobanModel:
    def __init__(self, maze_file: str) -> None:
        maze, player_stats = read_file(maze_file)
        self.maze, self.entities, player_position = convert_maze(maze)
        self.player = Player(player_stats[0], player_stats[1])
        self.player_position = player_position

    def get_maze(self) -> Grid:
        return self.maze

    def get_entities(self) -> Entities:
        return self.entities

    def get_player_position(self) -> Tuple[int, int]:
        return self.player_position

    def get_player_moves_remaining(self) -> int:
        return self.player.get_moves_remaining()

    def get_player_strength(self) -> int:
        return self.player.get_strength()

    def attempt_move(self, direction: str) -> bool:
        current_row, current_col = self.player_position

        if direction not in DIRECTION_DELTAS:
            return False

        delta_row, delta_col = DIRECTION_DELTAS[direction]

        new_row, new_col = current_row + delta_row, current_col + delta_col

        if not (0 <= new_row < len(self.maze)) or not (0 <= new_col < len(self.maze[0])):
            return False

        new_tile = self.maze[new_row][new_col]

        if isinstance(new_tile, Tile) and new_tile.is_blocking():
            return False

        if isinstance(new_tile, Crate):
            crate_strength = new_tile.get_strength()

            if self.player.get_strength() >= crate_strength:
                push_row, push_col = new_row + delta_row, new_col + delta_col

                if (
                        0 <= push_row < len(self.maze) and
                        0 <= push_col < len(self.maze[0]) and
                        (isinstance(self.maze[push_row][push_col], Tile) and not self.maze[push_row][
                            push_col].is_blocking()) and
                        (push_row, push_col) not in self.entities
                ):
                    self.entities[(push_row, push_col)] = self.entities.pop((new_row, new_col))
                    self.maze[push_row][push_col] = self.maze[new_row][new_col]
                else:
                    return False

            else:
                return False

        self.player_position = (new_row, new_col)

        self.player.add_moves_remaining(-1)

        return True

    def has_won(self) -> bool:
        num_crates = 0
        num_filled_goals = 0

        for row in self.maze:
            for tile in row:
                if isinstance(tile, Crate):
                    num_crates += 1
                elif isinstance(tile, Goal) and tile.is_filled():
                    num_filled_goals += 1

        return num_crates == num_filled_goals


class Sokoban:
    def __init__(self, maze_file: str) -> None:
        self.model = SokobanModel(maze_file)
        self.view = SokobanView()

    def display(self) -> None:
        maze = self.model.get_maze()
        entities = self.model.get_entities()
        player_position = self.model.get_player_position()

        self.view.display_game(maze, entities, player_position)
        self.view.display_stats(self.model.get_player_moves_remaining(), self.model.get_player_strength())

    def play_game(self) -> None:
        while True:
            if self.model.has_won():
                self.display()
                print('You won!')
                return

            if not self.model.has_won() or self.model.get_player_moves_remaining() != 0:
                self.display()
                move = input('Enter move: ')

                if move == 'q':
                    return
                else:
                    success = self.model.attempt_move(move)

                    if not success:
                        print('Invalid move\n')
                continue

            print('You lost!')
            return


def main():
    # uncomment the lines below once you've written your Sokoban class
    game = Sokoban('maze_files/maze1.txt')
    game.play_game()
    pass


if __name__ == '__main__':
    main()
