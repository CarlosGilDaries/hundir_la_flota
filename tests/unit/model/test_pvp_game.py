import pytest
from model.result import ShotResult
from model.board import Board
from model.ship import Ship
from model.game.pvp_game import PvPGame, GameState
from tests.helpers import count_ship_cells, total_ship_characters
from unittest.mock import patch

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def test_ship_size_3():
    """Returns a size-3 ship for placement tests."""
    return Ship("Test", 3, "T")


@pytest.fixture
def pvp_game():
    """Creates a PVP game with two 6x6 boards and three ships per player."""
    player1_ships = [
        Ship("Test", 1, "P"),
        Ship("Launch", 2, "L"),
        Ship("Submarine", 3, "S")
    ]

    player2_ships = [
        Ship("Test", 1, "P"),
        Ship("Launch", 2, "L"),
        Ship("Submarine", 3, "S")
    ]

    board1 = Board(6, 6, player1_ships, "~", "X", "O")
    board2 = Board(6, 6, player2_ships, "~", "X", "O")

    return PvPGame(board1, board2)


@pytest.fixture
def pvp_game_one_ship_per_board_not_placed():
    """Creates a PVP game where each player has a single size-1 ship not placed."""
    player1_ships = [Ship("Test", 1, "P")]
    player2_ships = [Ship("Test", 1, "P")]

    board1 = Board(6, 6, player1_ships, "~", "X", "O")
    board2 = Board(6, 6, player2_ships, "~", "X", "O")

    return PvPGame(board1, board2)


@pytest.fixture
def boards_with_manually_placed_ships():
    """Creates two boards with several ships manually placed at known positions."""
    board1 = Board(6, 6, [
        Ship("Test", 1, "P", True),
        Ship("Launch", 2, "L", True),
        Ship("Submarine", 3, "S", True)
    ], "~", "X", "O")

    board2 = Board(6, 6, [
        Ship("Test", 1, "P", True),
        Ship("Destroyer", 3, "L", True),
        Ship("Submarine", 3, "S", True)
    ], "~", "X", "O")

    y = 0
    for ship in board1.ships:
        board1.place_ship_manually(ship, 0, y)
        y += 1

    y = 0
    for ship in board2.ships:
        board2.place_ship_manually(ship, 0, y)
        y += 1

    return [board1, board2]


@pytest.fixture
def boards_with_one_small_ship():
    """Creates two boards with a size-1 ship manually placed at a known position."""
    board1 = Board(6, 6, [Ship("Test", 1, "T", True)], "~", "X", "O")
    board2 = Board(6, 6, [Ship("Test", 1, "T", True)], "~", "X", "O")

    board1.place_ship_manually(board1.ships[0], 0, 0)
    board2.place_ship_manually(board2.ships[0], 0, 0)

    return [board1, board2]


@pytest.fixture
def game_with_placed_ships_turn_player_1(boards_with_manually_placed_ships):
    """Creates a game in PLAYING state with ships already placed and initial turn for player 1."""
    board1, board2 = boards_with_manually_placed_ships
    game = PvPGame(board1, board2)
    game._state = GameState.PLAYING
    return game


@pytest.fixture
def game_with_one_ship_placed_turn_player_1(boards_with_one_small_ship):
    """Creates a game in PLAYING state where each player has one ship placed."""
    board1, board2 = boards_with_one_small_ship
    game = PvPGame(board1, board2)
    game._state = GameState.PLAYING
    return game


class TestPvPGame:
    """Class responsible for testing the logic of a PvPGame."""

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================
    def test_constructor(self, pvp_game):
        """Checks that the constructor correctly initializes game attributes."""
        assert isinstance(pvp_game._boards, dict)
        assert len(pvp_game._boards) == 2
        assert pvp_game.current_turn() == 1
        assert pvp_game.state() == GameState.PLACEMENT
        assert isinstance(pvp_game._ready_players, set)
        assert len(pvp_game._ready_players) == 0

    # ============================================================================
    # SHOTS
    # ============================================================================

    @pytest.mark.parametrize("player, x, y, expected", [
        (1, 0, 1, ShotResult.HIT),
        (1, 0, 2, ShotResult.HIT),
    ])
    def test_shot_hit(self, game_with_placed_ships_turn_player_1, player, x, y, expected):
        """Verifies that a shot on a ship cell returns HIT."""
        assert game_with_placed_ships_turn_player_1.shoot(player, x, y) == expected


    def test_shot_sunk(self, game_with_placed_ships_turn_player_1):
        """Checks that shooting the last segment of a ship returns SUNK."""
        assert game_with_placed_ships_turn_player_1.shoot(1, 0, 0) == ShotResult.SUNK


    def test_shot_repeated(self, game_with_placed_ships_turn_player_1):
        """Verifies that shooting the same cell twice returns REPEATED."""
        game_with_placed_ships_turn_player_1.shoot(1, 0, 0)
        game_with_placed_ships_turn_player_1.shoot(2, 0, 0)
        assert game_with_placed_ships_turn_player_1.shoot(1, 0, 0) == ShotResult.REPEATED
        assert game_with_placed_ships_turn_player_1.shoot(2, 0, 0) == ShotResult.REPEATED


    def test_shot_invalid(self, game_with_placed_ships_turn_player_1):
        """Checks that shooting outside board boundaries returns INVALID."""
        assert game_with_placed_ships_turn_player_1.shoot(1, -10, 0) == ShotResult.INVALID
        assert game_with_placed_ships_turn_player_1.shoot(2, 0, 12) == ShotResult.INVALID

    # ============================================================================
    # SHOT / TURN / STATE
    # ============================================================================

    def test_shoot_changes_turn(self, game_with_placed_ships_turn_player_1):
        """Verifies that after a valid shot the turn switches to the opponent."""
        assert game_with_placed_ships_turn_player_1.current_turn() == 1
        game_with_placed_ships_turn_player_1.shoot(1, 0, 0)
        assert game_with_placed_ships_turn_player_1.current_turn() == 2
        game_with_placed_ships_turn_player_1.shoot(2, 0, 0)
        assert game_with_placed_ships_turn_player_1.current_turn() == 1


    def test_shoot_out_of_turn(self, game_with_placed_ships_turn_player_1):
        """Checks that shooting when it is not the player's turn raises ValueError."""
        with pytest.raises(ValueError):
            game_with_placed_ships_turn_player_1.shoot(2, 0, 0)  # Player 2 shoots on player 1's turn

        game_with_placed_ships_turn_player_1.shoot(1, 0, 0)      # Player 1 shoots and turn changes

        with pytest.raises(ValueError):
            game_with_placed_ships_turn_player_1.shoot(1, 0, 0)  # Player 1 tries to shoot on player 2's turn


    def test_shoot_when_state_not_playing(self, pvp_game):
        """Verifies that shooting is not allowed if the game is not in PLAYING state."""
        with pytest.raises(ValueError):
            pvp_game.shoot(1, 0, 0)  # Turn player 1 but state == GameState.PLACEMENT


    # ============================================================================
    # STATE / TURN
    # ============================================================================

    def test_state(self, pvp_game, game_with_one_ship_placed_turn_player_1):
        """Checks that the state method correctly returns the current game state."""
        assert pvp_game.state() == GameState.PLACEMENT
        assert game_with_one_ship_placed_turn_player_1.state() == GameState.PLAYING


    def test_current_turn(self, game_with_placed_ships_turn_player_1):
        """Verifies that current_turn correctly reflects turn changes after shooting."""
        assert game_with_placed_ships_turn_player_1.current_turn() == 1
        game_with_placed_ships_turn_player_1.shoot(1, 0, 0)
        assert game_with_placed_ships_turn_player_1.current_turn() == 2


    def test_all_sunk_ends_game(self, game_with_one_ship_placed_turn_player_1):
        """Checks that the game transitions to FINISHED when all ships are sunk."""
        assert game_with_one_ship_placed_turn_player_1.state() != GameState.FINISHED
        game_with_one_ship_placed_turn_player_1.shoot(1, 0, 0)
        assert game_with_one_ship_placed_turn_player_1.state() == GameState.FINISHED


    def test_check_victory_player(self, game_with_one_ship_placed_turn_player_1):
        """Verifies that check_victory returns True when the opponent's ships are sunk."""
        assert game_with_one_ship_placed_turn_player_1.check_victory() is False
        game_with_one_ship_placed_turn_player_1.shoot(1, 0, 0)
        assert game_with_one_ship_placed_turn_player_1.check_victory() is True


    def test_winning_player(self, game_with_one_ship_placed_turn_player_1):
        """Checks that winning_player returns the player who sinks the last opponent ship."""
        assert game_with_one_ship_placed_turn_player_1.winning_player() is None
        game_with_one_ship_placed_turn_player_1.shoot(1, 0, 0)
        assert game_with_one_ship_placed_turn_player_1.winning_player() == 1


    # ============================================================================
    # BOARD DISPLAY
    # ============================================================================

    def test_get_own_board_shows_ships(self, game_with_placed_ships_turn_player_1):
        """Verifies that get_own_board shows the player's ships."""
        board_player1 = game_with_placed_ships_turn_player_1.get_own_board(1)
        board_player2 = game_with_placed_ships_turn_player_1.get_own_board(2)

        assert total_ship_characters(game_with_placed_ships_turn_player_1._boards[1].ships) == count_ship_cells(board_player1) == 6
        assert total_ship_characters(game_with_placed_ships_turn_player_1._boards[2].ships) == count_ship_cells(board_player2) == 7


    def test_get_opponent_board_hides_ships(self, game_with_placed_ships_turn_player_1):
        """Checks that get_opponent_board hides the opponent's ships."""
        opponent_board_player1 = game_with_placed_ships_turn_player_1.get_opponent_board(1)  # Player 1 sees player 2's board
        opponent_board_player2 = game_with_placed_ships_turn_player_1.get_opponent_board(2)  # Player 2 sees player 1's board

        assert count_ship_cells(opponent_board_player1) == 0
        assert count_ship_cells(opponent_board_player2) == 0


    # ============================================================================
    # SHIP PLACEMENT
    # ============================================================================

    def test_place_ship(self, pvp_game):
        """Verifies that place_ship correctly places a ship on the board."""
        player1_ships = pvp_game._boards[1].ships
        assert pvp_game.place_ship(player1_ships[1], 0, 0, True, 1) is True


    def test_place_ship_on_occupied_cell(self, pvp_game):
        """Checks that a ship cannot be placed on top of another ship."""
        player1_ships = pvp_game._boards[1].ships
        assert pvp_game.place_ship(player1_ships[1], 0, 0, True, 1) is True
        assert pvp_game.place_ship(player1_ships[2], 0, 0, True, 1) is False


    def test_place_ship_out_of_bounds(self, pvp_game):
        """Verifies that a ship cannot be placed outside the board boundaries."""
        player1_ships = pvp_game._boards[1].ships
        assert pvp_game.place_ship(player1_ships[2], 10, 10, True, 1) is False
        assert pvp_game.place_ship(player1_ships[2], 6, 6, True, 1) is False


    @pytest.mark.parametrize("x, y, expected", [
        (0, 0, "T"),
        (1, 0, "T"),
        (2, 0, "T"),
        (3, 0, "~")
    ])
    def test_place_ship_horizontal(self, pvp_game, test_ship_size_3, x, y, expected):
        """Checks that a horizontal ship occupies the correct cells on the board."""
        pvp_game.place_ship(test_ship_size_3, 0, 0, True, 1)
        board_player1 = pvp_game.get_own_board(1)
        assert board_player1[y][x] == expected


    @pytest.mark.parametrize("x, y, expected", [
        (0, 0, "T"),
        (0, 1, "T"),
        (0, 2, "T"),
        (0, 3, "~")
    ])
    def test_place_ship_vertical(self, pvp_game, test_ship_size_3, x, y, expected):
        """Checks that a vertical ship occupies the correct cells on the board."""
        pvp_game.place_ship(test_ship_size_3, 0, 0, False, 1)
        board_player1 = pvp_game.get_own_board(1)
        assert board_player1[y][x] == expected


    # ============================================================================
    # PLACEMENT / STATE / TURN
    # ============================================================================

    def test_all_placed_adds_player_to_ready_players(self, pvp_game_one_ship_per_board_not_placed):
        """Verifies that a player is added to ready_players when all their ships are placed."""
        assert len(pvp_game_one_ship_per_board_not_placed._ready_players) == 0

        player2_ships = pvp_game_one_ship_per_board_not_placed._boards[2].ships
        pvp_game_one_ship_per_board_not_placed.place_ship(player2_ships[0], 0, 0, False, 2)
        assert len(pvp_game_one_ship_per_board_not_placed._ready_players) == 1
        assert 2 in pvp_game_one_ship_per_board_not_placed._ready_players


    def test_ready_players_changes_state_to_playing(self, pvp_game_one_ship_per_board_not_placed):
        """Checks that the state transitions to PLAYING when both players have placed their ships."""
        assert pvp_game_one_ship_per_board_not_placed.state() != GameState.PLAYING

        player2_ships = pvp_game_one_ship_per_board_not_placed._boards[2].ships
        player1_ships = pvp_game_one_ship_per_board_not_placed._boards[1].ships
        pvp_game_one_ship_per_board_not_placed.place_ship(player2_ships[0], 0, 0, False, 2)
        pvp_game_one_ship_per_board_not_placed.place_ship(player1_ships[0], 0, 0, False, 1)
        assert len(pvp_game_one_ship_per_board_not_placed._ready_players) == 2
        assert pvp_game_one_ship_per_board_not_placed.state() == GameState.PLAYING


    def test_ready_players_randomizes_turn(self, pvp_game_one_ship_per_board_not_placed):
        """Verifies that the first turn is randomized when both players are ready."""
        player2_ships = pvp_game_one_ship_per_board_not_placed._boards[2].ships
        player1_ships = pvp_game_one_ship_per_board_not_placed._boards[1].ships

        pvp_game_one_ship_per_board_not_placed.place_ship(player2_ships[0], 0, 0, False, 2)
        with patch("model.game.pvp_game.random.randint", return_value=2):
            pvp_game_one_ship_per_board_not_placed.place_ship(player1_ships[0], 0, 0, False, 1)
        assert pvp_game_one_ship_per_board_not_placed.current_turn() == 2