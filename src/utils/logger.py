import logging
import sys
from pathlib import Path

def get_logger(name: str, log_file: str = "app.log", level: int = logging.INFO) -> logging.Logger:
    """
    Creates and configures a structured logger.
    
    Args:
        name (str): Name of the logger (usually __name__).
        log_file (str, optional): The file to which logs should be written. Defaults to "app.log".
        level (int, optional): The logging level. Defaults to logging.INFO.
        
    Returns:
        logging.Logger: A configured standard library Logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if the logger is already configured
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    # Define a standard, structured format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    try:
        # Ensure the logs directory exists if a path with directories is provided
        log_path = Path(log_file)
        if log_path.parent != Path("."):
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, log it to the console (which is already set up)
        logger.warning(f"Failed to set up file logging to {log_file}: {e}")

    return logger
