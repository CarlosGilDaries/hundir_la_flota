import pytest
from model.ship import Ship

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(params=[
    ("Launch", 2, "L", None),
    ("Submarine", 3, "S", False),
    ("Battleship", 4, "A", True),
    ("Aircraft Carrier", 5, "P", None),
])
def ship(request):
    """Fixture that returns different Ship instances."""
    name, size, character, horizontal = request.param
    return Ship(name, size, character, horizontal)


class TestShip:
    """Tests for the Ship class behavior."""


    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================

    def test_constructor_attributes(self, ship):
        """Verifies that basic attributes are initialized correctly."""
        assert ship.name in ["Launch", "Submarine", "Battleship", "Aircraft Carrier"]
        assert ship._remaining_health == ship.size
        assert isinstance(ship.character, str)


    # ============================================================================
    # ORIENTATION
    # ============================================================================

    def test_constructor_horizontal(self, ship):
        """Checks that the initial orientation is a boolean."""
        assert isinstance(ship.get_horizontal(), bool)


    @pytest.mark.parametrize("horizontal", [True, False])
    def test_set_horizontal(self, ship, horizontal):
        """Verifies that orientation can be set manually."""
        ship.set_horizontal(horizontal)
        assert ship.get_horizontal() is horizontal


    def test_set_horizontal_random(self, ship):
        """Verifies that random orientation is assigned if not specified."""
        ship.set_horizontal(None)
        assert isinstance(ship.get_horizontal(), bool)


    # ============================================================================
    # MAXIMUM POSITION
    # ============================================================================

    @pytest.mark.parametrize("dimension", [8, 10, 12])
    def test_calculate_max_position(self, ship, dimension):
        """Checks the calculation of the ship's maximum position."""
        expected = dimension - ship.size
        assert ship.calculate_max_position(dimension) == expected


    # ============================================================================
    # HITS
    # ============================================================================

    def test_take_hit(self, ship):
        """Verifies that remaining health decreases when a hit is taken."""
        initial_health = ship._remaining_health
        ship.take_hit()
        assert ship._remaining_health == initial_health - 1


    def test_is_sunk(self, ship):
        """Checks that the ship is only considered sunk when its health is 0."""
        while ship._remaining_health > 0:
            assert ship.is_sunk() is False
            ship.take_hit()

        assert ship.is_sunk() is True