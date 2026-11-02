import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

from core.settings import LogSettings


class Logger:
    """
    Singleton logger class with file rotation and dynamic log level control.
    Handles both console and file logging with different levels.
    """

    _instance: Optional["Logger"] = None
    _handlers_initialized: bool = False
    _force_debug: bool = False

    def __init__(self, logger_config: LogSettings):
        self.config = logger_config
        self._setup_logging()

    def _setup_logging(self):
        """
        Initialize logging handlers with rotation.
        Creates separate handlers for info, errors, debug, and console output.
        """
        if Logger._handlers_initialized:
            return

        log_dir = self.config.get_log_file_path()
        log_dir.mkdir(exist_ok=True, parents=True)

        formatter = logging.Formatter(self.config.system_format)

        log_level = self.config.log_level
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        def make_handler(filename: str, level: int) -> RotatingFileHandler:
            """Create a rotating file handler with specified level."""
            handler = RotatingFileHandler(
                filename=log_dir / filename,
                maxBytes=self.config.max_bytes,
                backupCount=self.config.backup_count,
                encoding=self.config.encoding,
            )
            handler.setFormatter(formatter)
            handler.setLevel(level)
            return handler

        class InfoFilter(logging.Filter):
            """Filter that only passes INFO level messages (not ERROR or above)."""

            def filter(self, record):
                return logging.INFO <= record.levelno < logging.ERROR

        # Handler for INFO level messages only
        info_handler = make_handler("info.log", logging.INFO)
        info_handler.addFilter(InfoFilter())
        root_logger.addHandler(info_handler)

        # Handler for ERROR level messages and above
        error_handler = make_handler("errors.log", logging.ERROR)
        root_logger.addHandler(error_handler)

        # Handler for DEBUG level messages (optional)
        if self.config.debug:
            debug_handler = make_handler("debug.log", logging.DEBUG)
            root_logger.addHandler(debug_handler)

        # Console handler for real-time output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

        # Store handlers for dynamic level adjustment
        self._info_handler = info_handler
        self._error_handler = error_handler
        self._debug_handler = debug_handler if self.config.debug else None
        self._console_handler = console_handler

        Logger._handlers_initialized = True

    def set_log_level(self, level: int) -> None:
        """
        Change the log level for all handlers and the root logger.

        Args:
            level: Log level (logging.DEBUG, logging.INFO, etc.)
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Update console handler level
        if hasattr(self, "_console_handler") and self._console_handler:
            self._console_handler.setLevel(level)

        # Update file handlers levels
        if hasattr(self, "_info_handler") and self._info_handler:
            # Info handler should continue filtering INFO and above
            # But its level can be raised
            self._info_handler.setLevel(min(level, logging.INFO))

        if hasattr(self, "_error_handler") and self._error_handler:
            self._error_handler.setLevel(min(level, logging.ERROR))

        if hasattr(self, "_debug_handler") and self._debug_handler:
            self._debug_handler.setLevel(level)

        logger = logging.getLogger(__name__)
        logger.info(f"Log level changed to {logging.getLevelName(level)}")

    def set_debug_mode(self, enabled: bool = True) -> None:
        """
        Enable or disable DEBUG mode.

        Args:
            enabled: True - enable DEBUG, False - disable DEBUG
        """
        if enabled:
            self.set_log_level(logging.DEBUG)
            # Create debug handler if it wasn't created during initialization
            if not self._debug_handler and not self.config.debug:
                self._add_debug_handler()
        else:
            self.set_log_level(self.config.log_level)

    def _add_debug_handler(self) -> None:
        """Add a debug handler for DEBUG level logs if it doesn't exist."""
        log_dir = self.config.get_log_file_path()
        formatter = logging.Formatter(self.config.system_format)

        debug_handler = RotatingFileHandler(
            filename=log_dir / "debug.log",
            maxBytes=self.config.max_bytes,
            backupCount=self.config.backup_count,
            encoding=self.config.encoding,
        )
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()
        root_logger.addHandler(debug_handler)
        self._debug_handler = debug_handler

        logger = logging.getLogger(__name__)
        logger.info("Debug logging enabled")

    def get_current_log_level(self) -> int:
        """Return the current effective log level of the root logger."""
        return logging.getLogger().getEffectiveLevel()

    def enable_logger_for_test(self, logger_name: str, level: int = logging.DEBUG) -> None:
        """
        Enable detailed logging for a specific logger (useful for tests).

        Args:
            logger_name: Logger name (e.g., 'app.service.repository')
            level: Log level to set
        """
        test_logger = logging.getLogger(logger_name)
        test_logger.setLevel(level)

        # Add a console handler for tests if not already present
        if not any(
            isinstance(h, logging.StreamHandler) and h.level <= level for h in test_logger.handlers
        ):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(logging.Formatter(self.config.system_format))
            test_logger.addHandler(console_handler)

    def disable_logging_for_test(self) -> None:
        """Disable all logging (useful for clean test output)."""
        logging.disable(logging.CRITICAL)

    def enable_logging_for_test(self) -> None:
        """Re-enable logging after disable_logging_for_test()."""
        logging.disable(logging.NOTSET)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance by name.

        Args:
            name: Logger name (typically __name__)

        Works before init_logger(): the handlers are attached to the root logger.

        Returns:
            logging.Logger instance
        """
        return logging.getLogger(name)

    @classmethod
    def init_logger(cls, logger_config: LogSettings) -> "Logger":
        """
        Initialize the singleton logger instance.

        Args:
            logger_config: Logger configuration object

        Returns:
            Logger singleton instance
        """
        if not cls._instance:
            cls._instance = cls(logger_config)
        return cls._instance
