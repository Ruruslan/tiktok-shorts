import logging

SENSITIVE_KEYS = {'authorization', 'openai_api_key', 'csrf_token'}


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = str(record.msg)
        for key in SENSITIVE_KEYS:
            if key in message.lower():
                record.msg = '[redacted sensitive log message]'
                break
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
    for handler in root.handlers:
        handler.addFilter(RedactingFilter())
