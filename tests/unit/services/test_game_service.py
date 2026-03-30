import pytest
from model.result import ShotResult
from model.game.pvp_game import PvPGame, GameState
from services.game_service import GameService


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def game_service():
    """Returns a GameService instance."""
    config = {
        "width": 10,
        "height": 10,
        "ships": [
            ("Aircraft Carrier", 5, "P"),
            ("Battleship", 4, "A"),
            ("Destroyer", 3, "D"),
            ("Submarine", 3, "S"),
            ("Launch", 2, "L"),
        ]
    }
    characters = {
        "EMPTY_CHARACTER": "~",
        "HIT_CHARACTER": "X",
        "WATER_CHARACTER": "O"
    }

    return GameService(config, characters)


@pytest.fixture
def game_service_with_one_size_1_ship_placed():
    """Returns a GameService instance with a size-1 ship placed at a known position for each player."""
    config = {
        "width": 10,
        "height": 10,
        "ships": [
            ("Test", 1, "T"),
        ]
    }
    characters = {
        "EMPTY_CHARACTER": "~",
        "HIT_CHARACTER": "X",
        "WATER_CHARACTER": "O"
    }
    game = GameService(config, characters)

    for player in [1, 2]:
        for ship in game.remaining_ships(player):
            game.place_ship(player, 1, 0, 0, True)

    return game


class TestGameService:
    """Tests for GameService."""

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================

    def test_constructor_creates_ships_correctly(self, game_service):
        """Checks that ships are created with the correct configuration data."""
        for ship, config_ship in zip(game_service.player1_ships, game_service.config["ships"]):
            name, size, char = config_ship
            assert ship.name == name
            assert ship.size == size
            assert ship.character == char

        for ship, config_ship in zip(game_service.player2_ships, game_service.config["ships"]):
            name, size, char = config_ship
            assert ship.name == name
            assert ship.size == size
            assert ship.character == char

        # Ships of player 1 and player 2 must be distinct objects
        for ship1, ship2 in zip(game_service.player1_ships, game_service.player2_ships):
            assert ship1 is not ship2


    def test_constructor_independent_copies(self, game_service):
        """Checks that the pending lists are independent copies."""
        assert game_service.player1_ships is not game_service.remaining_ships(1)
        assert game_service.player2_ships is not game_service.remaining_ships(2)
        assert game_service.remaining_ships(1) is not game_service.remaining_ships(2)

        # Modifying pending does not affect original ships
        original_len = len(game_service.player1_ships)
        game_service.remaining_ships(1).pop()
        assert len(game_service.player1_ships) == original_len


    def test_constructor_creates_game_correctly(self, game_service):
        """Checks that the game is created with correct boards and initial state."""
        game = game_service._game

        assert isinstance(game, PvPGame)
        assert game.state() == GameState.PLACEMENT
        assert game.current_turn() == 1

        board1 = game._boards[1]
        board2 = game._boards[2]

        assert board1.width == game_service.config["width"]
        assert board1.height == game_service.config["height"]
        assert board2.width == game_service.config["width"]
        assert board2.height == game_service.config["height"]


    # ============================================================================
    # REMAINING SHIPS
    # ============================================================================

    def test_remaining_ships_length(self, game_service):
        """Checks that it returns the correct number of pending ships."""
        assert len(game_service.remaining_ships(1)) == len(game_service.config["ships"])


    def test_remaining_ships_format(self, game_service):
        """Checks that the output format of remaining_ships is correct."""
        ship = game_service.remaining_ships(1)[0]

        assert isinstance(ship, dict)
        assert set(ship.keys()) == {"index", "name", "size"}


    # ============================================================================
    # SHIP PLACEMENT
    # ============================================================================

    def test_valid_placement_removes_from_pending(self, game_service):
        """Checks that a valid ship placement removes it from pending."""
        initial = len(game_service.remaining_ships(1))

        result = game_service.place_ship(1, 1, 0, 0, True)

        assert result is True
        assert len(game_service.remaining_ships(1)) == initial - 1


    def test_invalid_placement_does_not_remove_from_pending(self, game_service):
        """Checks that an invalid placement does not remove the ship."""
        initial = len(game_service.remaining_ships(1))

        game_service.place_ship(1, 1, 999, 999, True)

        assert len(game_service.remaining_ships(1)) == initial


    def test_invalid_index_raises_error(self, game_service):
        """Checks that an invalid index raises ValueError."""
        with pytest.raises(ValueError):
            game_service.place_ship(1, 0, 0, 0, True)


    def test_index_corresponds_to_correct_ship(self, game_service):
        """Checks that the index corresponds to the correct ship."""
        ships = game_service.remaining_ships(1)
        first_name = ships[0]["name"]

        game_service.place_ship(1, 1, 0, 0, True)

        remaining = game_service.remaining_ships(1)
        assert all(ship["name"] != first_name for ship in remaining)


    # =============================================================================
    # SHOT (DELEGATION)
    # =============================================================================

    def test_shoot_returns_valid_result(self, game_service_with_one_size_1_ship_placed):
        """Checks that shoot returns a valid ShotResult."""
        turn = game_service_with_one_size_1_ship_placed.current_turn()
        result = game_service_with_one_size_1_ship_placed.shoot(turn, 0, 0)

        assert result in ShotResult


    # =============================================================================
    # STATE AND BOARDS (DELEGATION)
    # =============================================================================

    def test_state(self, game_service):
        """Checks that state returns a valid GameState."""
        assert game_service.state() in GameState


    def test_get_boards_state_format(self, game_service):
        """Checks that get_boards_state returns the correct structure."""
        state = game_service.get_boards_state(1)

        assert "own" in state
        assert "opponent" in state
        assert isinstance(state["own"], list)
        assert isinstance(state["opponent"], list)


    # =============================================================================
    # END OF GAME
    # =============================================================================

    def test_check_victory_and_winning_player(self, game_service_with_one_size_1_ship_placed):
        """Checks that check_victory and winning_player work without errors."""
        assert game_service_with_one_size_1_ship_placed.check_victory() is False
        assert game_service_with_one_size_1_ship_placed.winning_player() is None

        turn = game_service_with_one_size_1_ship_placed.current_turn()
        game_service_with_one_size_1_ship_placed.shoot(turn, 0, 0)

        assert game_service_with_one_size_1_ship_placed.check_victory() is True
        assert game_service_with_one_size_1_ship_placed.winning_player() == turn