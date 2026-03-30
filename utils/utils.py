class Util:
    """
    Utility class that groups helper functions
    for validating user input.
    """

    @staticmethod
    def is_valid_option(value: str, max_option: int) -> bool:
        """
        Checks if a given value is an integer within a valid range.

        Args:
            value (str): Value entered by the user.
            max_option (int): Maximum allowed value.

        Returns:
            bool: True if the value is an integer within the allowed range,
            False otherwise.
        """
        return value.isdigit() and 0 <= int(value) <= max_option

    @staticmethod
    def is_integer(value: str) -> bool:
        """
        Checks if a value can be converted to an integer.

        Args:
            value (str): Value to check.

        Returns:
            bool: True if the value is a valid integer, False otherwise.
        """
        try:
            int(value)
            return True
        except ValueError:
            return False