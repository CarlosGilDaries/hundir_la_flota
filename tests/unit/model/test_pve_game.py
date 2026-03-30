import pytest
from model.result import ShotResult
from model.board import Board
from model.ship import Ship
from model.game.pve_game import PvEGame
from tests.helpers import count_ship_cells, total_ship_characters

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def ships():
    """Provides a list of test ships with different sizes."""
    return [
        Ship("Test", 1, "P"),
        Ship("Launch", 2, "L"),
        Ship("Submarine", 3, "S")
    ]


@pytest.fixture
def horizontal_ships():
    """Provides a list of ships configured with horizontal orientation."""
    return [
        Ship("Test", 1, "P", True),
        Ship("Launch", 2, "L", True),
        Ship("Submarine", 3, "S", True)
    ]


@pytest.fixture
def board(ships):
    """Creates an empty test board with the available ships."""
    return Board(6, 6, ships, "~", "X", "O")


@pytest.fixture
def board_with_manually_placed_ships(horizontal_ships):
    """Creates a board with ships manually placed at known positions."""
    board = Board(6, 6, horizontal_ships, "~", "X", "O")
    y = 0
    for ship in board.ships:
        board.place_ship_manually(ship, 0, y)
        y += 1
    return board


@pytest.fixture
def pve_game(board):
    """Creates a standard PvE game with ships automatically placed."""
    return PvEGame(board, 10)


@pytest.fixture
def game_with_few_shots(board):
    """Creates a PvE game with a very limited number of shots."""
    return PvEGame(board, 2)


@pytest.fixture
def game_with_placed_ships(board_with_manually_placed_ships):
    """Creates a PvE game with ships already manually placed for deterministic tests."""
    return PvEGame(board_with_manually_placed_ships, 10, True)


@pytest.fixture
def game_without_placed_ships(board):
    """Creates a PvE game with an empty board and no automatic ship placement."""
    return PvEGame(board, 10, True)


class TestPvEGame:
    """Class responsible for testing the logic of a PvEGame."""

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================
    def test_constructor(self, pve_game, board):
        """Verifies that the constructor initializes attributes and automatically places ships."""
        total_ship_characters_count = total_ship_characters(board.ships)

        assert pve_game.machine_board == board
        assert pve_game._max_shots == 10
        assert pve_game._shots_fired == 0
        assert count_ship_cells(pve_game.get_own_board()) == total_ship_characters_count


    # ============================================================================
    # SHOTS
    # ============================================================================

    @pytest.mark.parametrize("x, y, expected", [
        (0, 1, ShotResult.HIT),
        (0, 2, ShotResult.HIT),
    ])
    def test_shot_hit(self, game_with_placed_ships, x, y, expected):
        """Checks that shooting a cell with a ship returns HIT."""
        assert game_with_placed_ships.shoot(x, y) == expected


    def test_shot_sunk(self, game_with_placed_ships):
        """Checks that shooting a size-1 ship returns SUNK."""
        assert game_with_placed_ships.shoot(0, 0) == ShotResult.SUNK


    @pytest.mark.parametrize("x, y, expected", [
        (5, 5, ShotResult.WATER),
        (4, 4, ShotResult.WATER),
    ])
    def test_shot_water(self, game_with_placed_ships, x, y, expected):
        """Verifies that shooting an empty cell returns WATER."""
        assert game_with_placed_ships.shoot(x, y) == expected


    @pytest.mark.parametrize("x, y, expected", [
        (-2, 5, ShotResult.INVALID),
        (8, 4, ShotResult.INVALID),
    ])
    def test_shot_invalid(self, game_with_placed_ships, x, y, expected):
        """Checks that shooting outside board boundaries returns INVALID."""
        assert game_with_placed_ships.shoot(x, y) == expected


    def test_shot_repeated(self, game_with_placed_ships):
        """Verifies that shooting the same cell twice returns REPEATED."""
        game_with_placed_ships.shoot(0, 1)
        assert game_with_placed_ships.shoot(0, 1) == ShotResult.REPEATED


    # ============================================================================
    # SHOT COUNTS / REMAINING SHOTS
    # ============================================================================

    def test_has_shots_left(self, game_with_few_shots):
        """Verifies that the system correctly detects when shots are exhausted."""
        assert game_with_few_shots.has_shots_left() is True
        game_with_few_shots.shoot(0, 0)
        assert game_with_few_shots.has_shots_left() is True
        game_with_few_shots.shoot(0, 1)
        assert game_with_few_shots.has_shots_left() is False


    def test_remaining_shots(self, pve_game):
        """Checks that the number of remaining shots updates after each valid shot."""
        assert pve_game.remaining_shots() == pve_game._max_shots
        pve_game.shoot(0, 0)
        assert pve_game.remaining_shots() == pve_game._max_shots - pve_game._shots_fired
        pve_game.shoot(0, 1)
        assert pve_game.remaining_shots() == pve_game._max_shots - pve_game._shots_fired


    def test_shoot_increases_shots_fired(self, pve_game):
        """Checks that valid shots increase the shots fired counter."""
        pve_game.shoot(0, 0)
        assert pve_game._shots_fired == 1
        pve_game.shoot(0, 2)
        assert pve_game._shots_fired == 2


    def test_repeated_shot_does_not_increase_shots_fired(self, pve_game):
        """Verifies that repeating a shot does not increase the shots fired counter."""
        pve_game.shoot(0, 0)
        pve_game.shoot(0, 0)
        pve_game.shoot(0, 0)
        assert pve_game._shots_fired == 1


    def test_invalid_shot_does_not_increase_shots_fired(self, pve_game):
        """Checks that invalid shots do not increase the shots fired counter."""
        pve_game.shoot(-2, 0)
        pve_game.shoot(5, 12)
        assert pve_game._shots_fired == 0


    # ============================================================================
    # BOARD DISPLAY
    # ============================================================================

    def test_get_own_board_returns_ships(self, pve_game, ships):
        """Verifies that the own board shows the positions of the ships."""
        total_ship_characters_count = total_ship_characters(ships)
        board = pve_game.get_own_board()
        assert count_ship_cells(board) == total_ship_characters_count


    def test_get_opponent_board_does_not_return_ships(self, pve_game):
        """Checks that the board visible to the player does not reveal enemy ships."""
        board = pve_game.get_opponent_board()
        assert count_ship_cells(board) == 0


    def test_get_board_dimensions(self, ships):
        """Verifies that the game returns the correct board dimensions."""
        width = 10
        height = 10
        board = Board(width, height, ships, "~", "X", "O")
        game = PvEGame(board, 10)

        assert game.get_board_dimensions() == (width, height)


    # ============================================================================
    # SHIP PLACEMENT
    # ============================================================================

    def test_place_ship(self, game_without_placed_ships, ships):
        """Verifies that ships can be placed automatically on the board."""
        assert game_without_placed_ships.place_ship(ships[0]) is True
        assert game_without_placed_ships.place_ship(ships[1]) is True
        assert game_without_placed_ships.place_ship(ships[2]) is True


    # ============================================================================
    # VICTORY
    # ============================================================================

    def test_check_victory(self, game_with_placed_ships):
        """Checks that victory is detected only when all ships have been sunk."""
        shots = [(0, 0), (0, 1), (1, 1), (0, 2), (1, 2)]

        for x, y in shots:
            game_with_placed_ships.shoot(x, y)
            assert game_with_placed_ships.check_victory() is False

        game_with_placed_ships.shoot(2, 2)
        assert game_with_placed_ships.check_victory() is True