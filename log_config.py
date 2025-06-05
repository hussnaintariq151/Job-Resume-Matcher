import logging
import sys

def get_logger(name: str, log_file: str = None, level=logging.DEBUG) -> logging.Logger:
    """
    Creates and returns a logger instance.
    
    Args:
        name (str): Logger name.
        log_file (str, optional): If provided, logs will be written to this file.
        level (int): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding multiple handlers if this function is called multiple times
    if not logger.hasHandlers():
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler (optional)
        if log_file:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
    
    return logger
