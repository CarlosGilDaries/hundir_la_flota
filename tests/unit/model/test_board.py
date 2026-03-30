import pytest
from model.board import Board
from model.ship import Ship
from model.result import ShotResult

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def ships():
    """Provides a list of test ships with various sizes and horizontal orientation."""
    return [
        Ship("Launch", 2, "L", True),
        Ship("Submarine", 3, "S", True),
        Ship("Destroyer", 3, "D", True),
        Ship("Battleship", 4, "A", True),
        Ship("Aircraft Carrier", 5, "P", True),
    ]


@pytest.fixture
def board(ships):
    """Creates a test board."""
    return Board(10, 10, ships, "~", "X", "O")


@pytest.fixture
def empty_board():
    """Creates an empty test board with available ships."""
    ships = [
        Ship("Launch", 2, "L", True),
        Ship("Submarine", 3, "S", True),
    ]
    return Board(10, 10, ships, "~", "X", "O")


@pytest.fixture
def board_with_ships(empty_board):
    """Creates a test board with ships placed at known positions."""
    y = 0
    for ship in empty_board.ships:
        empty_board.place_ship_manually(ship, 0, y)
        y += 1
    return empty_board


class TestBoard:
    """Tests for the Board class behavior."""

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================
    def test_constructor(self, board):
        """Verifies that the constructor correctly initializes board attributes."""
        assert board.width == 10
        assert board.height == 10
        assert isinstance(board.ships, list)
        assert board._empty_character == "~"
        assert board._hit_character == "X"
        assert board._water_character == "O"
        assert board._placed_ships_count == 0

        for row in board.get_all_cells():
            assert all(cell is None for cell in row)


    # ============================================================================
    # SHOTS
    # ============================================================================

    @pytest.mark.parametrize("x, y, character", [
        (0, 0, "X"),
        (4, 5, "O"),
    ])
    def test_mark_shot(self, board, x, y, character):
        """Checks that mark_shot saves the character at the indicated cell."""
        board.mark_shot(x, y, character)
        assert board.get_cell(x, y) == character


    def test_shot_hit(self, empty_board):
        """Verifies that a shot on a ship returns HIT result."""
        ship = Ship("Launch", 2, "L", True)
        empty_board.place_ship_manually(ship, 0, 0)

        result = empty_board.receive_shot(0, 0)

        assert result == [ShotResult.HIT, "X"]


    def test_shot_sunk(self, empty_board):
        """Checks that a ship is marked as sunk after receiving all hits."""
        ship = Ship("Launch", 2, "L", True)
        empty_board.place_ship_manually(ship, 0, 0)

        empty_board.receive_shot(0, 0)
        result = empty_board.receive_shot(1, 0)

        assert result == [ShotResult.SUNK, "X"]


    def test_shot_repeated(self, empty_board):
        """Verifies that shooting twice at the same cell returns REPEATED."""
        ship = Ship("Launch", 2, "L", True)
        empty_board.place_ship_manually(ship, 0, 0)

        empty_board.receive_shot(0, 0)
        result = empty_board.receive_shot(0, 0)

        assert result == [ShotResult.REPEATED, "X"]

    @pytest.mark.parametrize("x,y", [
        (-1, 0),
        (0, -1),
        (20, 0),
        (0, 20),
    ])
    def test_shot_out_of_bounds(self, board, x, y):
        """Checks that shooting off the board returns INVALID result."""
        result = board.receive_shot(x, y)
        assert result == [ShotResult.INVALID, ""]


    def test_shot_water(self, board):
        """Verifies that a shot on an empty cell returns WATER."""
        result = board.receive_shot(5, 5)
        assert result == [ShotResult.WATER, "O"]


    # ============================================================================
    # SHIP PLACEMENT
    # ============================================================================

    @pytest.mark.parametrize("ship, x, y, expected", [
        (Ship("Launch", 2, "L", True), 0, 0, True),
        (Ship("Submarine", 3, "S", False), 5, 5, True),
        (Ship("Destroyer", 3, "D", True), 9, 0, False),
    ])
    def test_place_ship_manually(self, board, ship, x, y, expected):
        """Validates that place_ship_manually places the ship only if the position is valid."""
        result = board.place_ship_manually(ship, x, y)
        assert result is expected


    def test_place_ship_randomly(self, board, ships):
        """Checks that ships can be placed randomly on the board."""
        for ship in ships:
            assert board.place_ship_randomly(ship)

        assert board._placed_ships_count == len(ships)


    # ============================================================================
    # BOARD VIEWS
    # ============================================================================

    def test_view_board_shows_ships(self, board_with_ships):
        """Verifies that view_board shows the characters of placed ships."""
        view = board_with_ships.view_board()

        assert view[0][0] == "L"
        assert view[0][1] == "L"
        assert view[1][0] == "S"
        assert view[1][1] == "S"
        assert view[1][2] == "S"


    def test_view_board_shows_shots(self, board_with_ships):
        """Checks that view_board reflects shots made on the board."""
        board_with_ships.mark_shot(0, 0, "X")
        board_with_ships.mark_shot(5, 5, "O")

        view = board_with_ships.view_board()

        assert view[0][0] == "X"
        assert view[5][5] == "O"


    def test_view_opponent_board_hides_ships(self, board_with_ships):
        """Verifies that view_opponent_board hides ships and shows only empty cells."""
        view = board_with_ships.view_opponent_board()

        for row in view:
            for cell in row:
                assert cell == "~"


    def test_view_opponent_board_shows_shots(self, board_with_ships):
        """Checks that view_opponent_board shows only the shots made."""
        board_with_ships.mark_shot(0, 0, "X")
        board_with_ships.mark_shot(4, 4, "O")

        view = board_with_ships.view_opponent_board()

        assert view[0][0] == "X"
        assert view[4][4] == "O"


    # ============================================================================
    # BOARD CELL ACCESS
    # ============================================================================

    def test_get_all_cells(self, board_with_ships):
        """Checks that get_all_cells returns the complete board matrix."""
        cells = board_with_ships.get_all_cells()

        assert isinstance(cells[0][0], Ship)
        assert cells[5][5] is None


    def test_get_cell(self, board_with_ships):
        """Verifies that get_cell returns the correct content of a position."""
        assert isinstance(board_with_ships.get_cell(0, 0), Ship)
        assert board_with_ships.get_cell(5, 5) is None


    # ============================================================================
    # STATE CHECKS
    # ============================================================================

    def test_all_placed(self, board):
        """Checks that all_placed returns True when all ships are on the board."""
        y = 0

        for ship in board.ships:
            assert not board.all_placed()
            board.place_ship_manually(ship, 0, y)
            y += 1

        assert board.all_placed()


    def test_all_sunk(self, empty_board):
        """Verifies that all_sunk returns True when all ships have been destroyed."""
        y = 0

        for ship in empty_board.ships:
            empty_board.place_ship_manually(ship, 0, y)
            y += 1

        assert not empty_board.all_sunk()

        empty_board.receive_shot(0, 0)
        empty_board.receive_shot(1, 0)

        empty_board.receive_shot(0, 1)
        empty_board.receive_shot(1, 1)
        empty_board.receive_shot(2, 1)

        assert empty_board.all_sunk()