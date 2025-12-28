import logging.config

from app.core.logs.config import LOGGING_CONFIG_RESULT

logging.config.dictConfig(LOGGING_CONFIG_RESULT)

debug_logger = logging.getLogger('default_debug_logger')
info_logger = logging.getLogger('default_info_logger')
error_logger = logging.getLogger('default_error_logger')

