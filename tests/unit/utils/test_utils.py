import pytest
import logging
from unittest.mock import patch
from utils.utils import Util
from utils.exceptions import ReturnToMenu, ExitProgram
from utils.log import configure_logger
from utils.log_decorator import log_async


class TestUtilityIsValidOption:
    """Tests for the option validation method of Utility class."""

    @pytest.mark.parametrize("value, max_option, expected", [
        ("2", 10, True),
        ("0", 10, True),
        ("10", 10, True),
        ("-2", 10, False),
        ("12", 10, False),
        ("2.33", 10, False),
        ("H", 10, False),
        ("", 10, False),
        (" 2", 10, False),
        ("2 ", 10, False),
    ])
    def test_valid_option_full_range(self, value, max_option, expected):
        """Verifies validation with different values inside and outside range."""
        assert Util.is_valid_option(value, max_option) == expected


    def test_valid_option_zero_minimum(self):
        """Verifies that zero is the minimum valid option."""
        assert Util.is_valid_option("0", 5) is True


    def test_valid_option_negative_invalid(self):
        """Verifies that negative numbers are not valid."""
        assert Util.is_valid_option("-1", 10) is False


    def test_valid_option_equal_maximum(self):
        """Verifies that the maximum value is included in the range."""
        assert Util.is_valid_option("10", 10) is True


    def test_valid_option_greater_than_maximum(self):
        """Verifies that values greater than maximum are not valid."""
        assert Util.is_valid_option("11", 10) is False


    def test_valid_option_decimal_invalid(self):
        """Verifies that decimal numbers are not valid."""
        assert Util.is_valid_option("2.5", 10) is False


    def test_valid_option_letter_invalid(self):
        """Verifies that letters are not valid."""
        assert Util.is_valid_option("a", 10) is False


    def test_valid_option_special_character_invalid(self):
        """Verifies that special characters are not valid."""
        assert Util.is_valid_option("!", 10) is False


class TestUtilityIsInteger:
    """Tests for integer validation."""

    @pytest.mark.parametrize("value, expected", [
        ("2", True),
        ("0", True),
        ("-5", True),
        ("1000", True),
        ("2.33", False),
        ("H", False),
        ("2a", False),
        ("", False),
    ])
    def test_is_integer_full_range(self, value, expected):
        """Verifies integer identification for various values."""
        assert Util.is_integer(value) == expected


    def test_is_integer_positive(self):
        """Verifies that positive numbers are identified."""
        assert Util.is_integer("123") is True


    def test_is_integer_negative(self):
        """Verifies that negative numbers are identified."""
        assert Util.is_integer("-123") is True


    def test_is_integer_zero(self):
        """Verifies that zero is identified as an integer."""
        assert Util.is_integer("0") is True


    def test_is_integer_decimal(self):
        """Verifies that decimals are not integers."""
        assert Util.is_integer("3.14") is False


    def test_is_integer_empty(self):
        """Verifies that empty string is not an integer."""
        assert Util.is_integer("") is False


    def test_is_integer_letter(self):
        """Verifies that letters are not integers."""
        assert Util.is_integer("abc") is False


    def test_is_integer_mixed(self):
        """Verifies that mixed letters and numbers are not valid."""
        assert Util.is_integer("12a") is False


class TestCustomExceptions:
    """Tests for custom exceptions."""

    def test_exception_return_to_menu_raises(self):
        """Verifies that ReturnToMenu can be raised."""
        with pytest.raises(ReturnToMenu):
            raise ReturnToMenu()


    def test_exception_return_to_menu_is_exception(self):
        """Verifies that ReturnToMenu inherits from Exception."""
        assert issubclass(ReturnToMenu, Exception)


    def test_exception_return_to_menu_with_message(self):
        """Verifies that ReturnToMenu accepts a message."""
        message = "Returning to menu"
        with pytest.raises(ReturnToMenu, match=message):
            raise ReturnToMenu(message)


    def test_exception_exit_program_raises(self):
        """Verifies that ExitProgram can be raised."""
        with pytest.raises(ExitProgram):
            raise ExitProgram()


    def test_exception_exit_program_is_exception(self):
        """Verifies that ExitProgram inherits from Exception."""
        assert issubclass(ExitProgram, Exception)


    def test_exception_exit_program_with_message(self):
        """Verifies that ExitProgram accepts a message."""
        message = "Exiting program"
        with pytest.raises(ExitProgram, match=message):
            raise ExitProgram(message)


    def test_exceptions_distinct(self):
        """Verifies that both exceptions can be distinguished."""
        with pytest.raises(ReturnToMenu):
            raise ReturnToMenu()

        with pytest.raises(ExitProgram):
            raise ExitProgram()


class TestConfigureLogger:
    """Tests for the configure_logger function."""

    @pytest.fixture(autouse=True)
    def clean_loggers(self):
        """Cleans up all test loggers after each test."""
        yield
        # Remove handlers from all test loggers
        for name in ["test_logger_custom", "test_console", "test_file", "test_level", "test_no_duplicate", "test_singleton", "test_cleanup"]:
            logger = logging.getLogger(name)
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)


    def test_configure_logger_returns_logger(self):
        """Verifies that configure_logger returns a logger object."""
        logger = configure_logger()
        assert isinstance(logger, logging.Logger)


    def test_configure_logger_custom_name(self):
        """Verifies that a custom name can be specified."""
        name = "test_logger_custom"
        logger = configure_logger(name=name)
        assert logger.name == name


    def test_configure_logger_default_file(self):
        """Verifies that it uses the default file."""
        logger = configure_logger(name="test_default_file")
        assert len([h for h in logger.handlers if isinstance(h, logging.FileHandler)]) > 0


    def test_configure_logger_has_console_handler(self):
        """Verifies that the logger has a console handler."""
        logger = configure_logger(name="test_console")
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
        assert len(console_handlers) > 0


    def test_configure_logger_has_file_handler(self):
        """Verifies that the logger has a file handler."""
        logger = configure_logger(name="test_file")
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0


    def test_configure_logger_no_duplicate_handlers(self):
        """Verifies that it does not duplicate handlers on successive calls."""
        name = "test_no_duplicate"
        logger1 = configure_logger(name=name)
        handlers_1 = len(logger1.handlers)

        logger2 = configure_logger(name=name)
        handlers_2 = len(logger2.handlers)

        assert handlers_1 == handlers_2


    def test_configure_logger_level_info(self):
        """Verifies that the log level is INFO."""
        logger = configure_logger(name="test_level")
        assert logger.level == logging.INFO


    def test_configure_logger_same_instance(self):
        """Verifies that it returns the same instance for the same name."""
        name = "test_singleton"
        logger1 = configure_logger(name=name)
        logger2 = configure_logger(name=name)

        assert logger1 is logger2


    def test_configure_logger_console_has_formatter(self):
        """Verifies that the console handler has a formatter."""
        logger = configure_logger(name="test_formatter")
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
        assert len(console_handlers) > 0
        assert console_handlers[0].formatter is not None


    def test_configure_logger_can_log_messages(self):
        """Verifies that it can log messages correctly."""
        logger = configure_logger(name="test_log_messages")
        # Should not raise exception
        logger.info("Test message")
        assert True


class TestLogAsyncDecorator:
    """Tests for the log_async decorator."""

    @pytest.mark.asyncio
    async def test_log_async_executes_function_correctly(self):
        """Verifies that the decorated function runs."""
        @log_async
        async def test_function():
            return "result"

        result = await test_function()
        assert result == "result"


    @pytest.mark.asyncio
    async def test_log_async_preserves_positional_arguments(self):
        """Verifies that positional arguments are preserved."""
        @log_async
        async def add(a, b):
            return a + b

        result = await add(2, 3)
        assert result == 5


    @pytest.mark.asyncio
    async def test_log_async_preserves_keyword_arguments(self):
        """Verifies that keyword arguments are preserved."""
        @log_async
        async def greet(name, age=20):
            return f"{name} is {age}"

        result = await greet("John", age=25)
        assert result == "John is 25"


    @pytest.mark.asyncio
    async def test_log_async_preserves_function_name(self):
        """Verifies that the decorator preserves the function name."""
        @log_async
        async def special_function():
            pass

        assert special_function.__name__ == "special_function"


    @pytest.mark.asyncio
    async def test_log_async_catches_exception_and_propagates(self):
        """Verifies that it catches exceptions and propagates them."""
        @log_async
        async def function_with_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await function_with_error()


    @pytest.mark.asyncio
    async def test_log_async_logs_error(self):
        """Verifies that it logs errors to the logger."""
        with patch('utils.log_decorator.logger') as logger_mock:
            @log_async
            async def failing_function():
                raise RuntimeError("Expected error")

            try:
                await failing_function()
            except RuntimeError:
                pass

            logger_mock.error.assert_called()


    @pytest.mark.asyncio
    async def test_log_async_with_none_result(self):
        """Verifies that it handles functions that return None."""
        @log_async
        async def returns_none():
            pass

        result = await returns_none()
        assert result is None


    @pytest.mark.asyncio
    async def test_log_async_with_exception_and_message(self):
        """Verifies error message in exception."""
        with patch('utils.log_decorator.logger') as logger_mock:
            @log_async
            async def raises_error():
                raise KeyError("missing_key")

            try:
                await raises_error()
            except KeyError:
                pass

            # Verify that the error was logged
            assert logger_mock.error.called


    @pytest.mark.asyncio
    async def test_log_async_with_multiple_arguments(self):
        """Verifies with multiple positional and keyword arguments."""
        @log_async
        async def complex_function(a, b, c, d=10, e=20):
            return a + b + c + d + e

        result = await complex_function(1, 2, 3, d=5, e=10)
        assert result == 21


    @pytest.mark.asyncio
    async def test_log_async_preserves_return_type(self):
        """Verifies that it preserves return types correctly."""
        @log_async
        async def returns_list():
            return [1, 2, 3]

        result = await returns_list()
        assert isinstance(result, list)
        assert result == [1, 2, 3]


    @pytest.mark.asyncio
    async def test_log_async_preserves_dictionary_return(self):
        """Verifies that it preserves dictionaries in return."""
        @log_async
        async def returns_dict():
            return {"key": "value"}

        result = await returns_dict()
        assert isinstance(result, dict)
        assert result["key"] == "value"