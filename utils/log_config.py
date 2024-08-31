from dotenv import load_dotenv
import logging, logging_loki
import os

load_dotenv()


# single file config for logger which save log for loki, console and local files
def configure_logger():
    base_path = os.path.dirname(os.path.abspath(__file__).replace(os.path.sep, "/"))
    logger_path = os.path.join(base_path, "../", "logs")
    check_logger_path(logger_path)
    loki_formatter = logging.Formatter("%(levelname)s %(message)s")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # loki_handler = logging_loki.LokiHandler(
    #     url=os.getenv("LOGGER_URL"),
    #     tags={"application": os.getenv("LOGGER_APP")},
    #     version="1",
    # )
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f"{logger_path}/{os.getenv('LOGGER_APP')}.log")

    # loki_handler.setFormatter(loki_formatter)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(os.getenv("LOGGER_APP"))
    logger.setLevel(logging.INFO)
    # logger.addHandler(loki_handler)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def check_logger_path(path) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
