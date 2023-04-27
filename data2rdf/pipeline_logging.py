import logging


def set_global_logger(path):
    logging.basicConfig(
        filename=path,
        filemode="w+",
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
