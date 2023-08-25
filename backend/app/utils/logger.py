import logging
import sys
from datetime import datetime
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
def setup_logger(name: str = "ai_assistant") -> logging.Logger:
    """
    Setup logger with file and console handlers
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(
        f"logs/{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create default logger
logger = setup_logger()

def log_function_call(func_name: str, **kwargs):
    """
    Log function calls with parameters
    """
    logger.info(f"Function called: {func_name} with params: {kwargs}")

def log_error(error: Exception, context: str = ""):
    """
    Log errors with context
    """
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

def log_ai_interaction(user_id: int, message: str, response: str, intent: str):
    """
    Log AI interactions for analysis
    """
    logger.info(f"AI Interaction - User: {user_id}, Intent: {intent}, Message: {message[:100]}...")

def log_performance_metric(metric_name: str, value: float, user_id: int = None):
    """
    Log performance metrics
    """
    user_info = f"User: {user_id}" if user_id else "System"
    logger.info(f"Performance Metric - {metric_name}: {value} ({user_info})")
