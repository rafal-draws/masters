import os
import sys
import logging
import platform

def normalize_path(path: str) -> str:
    if platform.system() == "Linux":
        return path.replace("\\", "/")
    
    if platform.system() == "Windows":
        return path.replace("/", "\\").replace("\\\\", "\\")
    
    
    return path

def setup_logging(debug: bool):
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.INFO)  # Accept INFO and above

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.INFO)  # Only log INFO and above

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    stdout_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)

    logger.info("This is INFO and should appear.")
    logger.warning("This is WARNING and should appear.")

    logger.info("Trying to parse the args")
    
    if debug == True:
        logger.setLevel(logging.DEBUG)
        stdout_handler.setLevel(logging.DEBUG)
        logger.debug("DEBUG ON")

    return logger
    