from core.logger import Logger

# Module loggers are plain logging loggers; the handlers are attached by
# Logger.init_logger(get_settings().log) at the entry point (main.py, worker, scripts).
# Settings: from core.settings import get_settings
logger = Logger
