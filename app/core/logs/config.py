from typing import Any


LOGGING_CONFIG_RESULT: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_uvicorn_formatter': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access_uvicorn_formatter': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
        'generic_gunicorn_formatter': {
            'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
            'class': 'logging.Formatter',
        },
        'default_debug_formatter': {
            'format': '%(asctime)s.%(msecs)03d %(module)s:%(lineno)d [%(levelname)s] - %(message)s',  # noqa: E501
            'datefmt': '[%Y-%m-%d %H:%M:%S]',
            'class': 'logging.Formatter',
        },
        'default_info_formatter': {
            'format': '%(asctime)s.%(msecs)03d %(module)s:%(lineno)d [%(levelname)s] - %(message)s',  # noqa: E501
            'datefmt': '[%Y-%m-%d %H:%M:%S]',
            'class': 'logging.Formatter',
        },
        'default_error_formatter': {
            'format': '%(asctime)s.%(msecs)03d %(module)s:%(lineno)d [%(levelname)s] - %(message)s',  # noqa: E501
            'datefmt': '[%Y-%m-%d %H:%M:%S]',
            'class': 'logging.Formatter',
        },
    },
    'handlers': {
        'default_uvicorn_handler': {
            'formatter': 'default_uvicorn_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'access_uvicorn_handler': {
            'formatter': 'access_uvicorn_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'console_gunicorn_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic_gunicorn_formatter',
            'stream': 'ext://sys.stdout',
        },
        'error_console_gunicorn_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic_gunicorn_formatter',
            'stream': 'ext://sys.stderr',
        },
        'console_debug_handler': {
            'formatter': 'default_debug_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'DEBUG',
        },
        'console_info_handler': {
            'formatter': 'default_info_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'INFO',
        },
        'console_error_handler': {
            'formatter': 'default_error_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'uvicorn': {
            'handlers': ['default_uvicorn_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'uvicorn.error': {
            'level': 'INFO',
        },
        'uvicorn.access': {
            'handlers': ['access_uvicorn_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['error_console_gunicorn_handler'],
            'propagate': True,
            'qualname': 'gunicorn.error',
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['console_gunicorn_handler'],
            'propagate': True,
            'qualname': 'gunicorn.access',
        },
        'default_debug_logger': {
            'handlers': ['console_debug_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'default_info_logger': {
            'handlers': ['console_info_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'default_error_logger': {
            'handlers': ['console_error_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
