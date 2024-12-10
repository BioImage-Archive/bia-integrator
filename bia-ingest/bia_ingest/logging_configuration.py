import logging
from rich.logging import RichHandler

class TableLoggingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if "TABLE :::" in record.msg:
            return True
        else:
            return False

class ServerLoggingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if "TABLE :::" in record.msg:
            return False
        else:
            return True

server_handler = logging.FileHandler("server.log", mode="a", encoding="utf-8")
table_handler = logging.FileHandler("table.log", mode="w", encoding="utf-8")

server_log_formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
table_log_formatter = logging.Formatter('%(message)s')

server_handler.setFormatter(server_log_formatter)
table_handler.setFormatter(table_log_formatter)

table_log_filter = TableLoggingFilter()
table_handler.addFilter(table_log_filter)
server_log_filter = ServerLoggingFilter()
server_handler.addFilter(server_log_filter)

logging_config = logging
logging_config.basicConfig(
    level=logging.INFO, 
    format="%(message)s", 
    handlers=[RichHandler(show_time=False), server_handler, table_handler]
)
