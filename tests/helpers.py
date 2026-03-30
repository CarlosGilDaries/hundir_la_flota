def count_ship_cells(board):
    """Counts how many cells in the board contain ship parts."""
    count = 0
    for row in board:
        for cell in row:
            if cell not in ["~", "X", "O"]:
                count += 1
    return count


def total_ship_characters(ships_list):
    """Calculates the total number of cells that all ships should occupy."""
    return sum(ship.size for ship in ships_list)