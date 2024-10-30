import configparser
import logging

def load_config():
    # Load configuration from config.ini
    config = configparser.ConfigParser()
    try:
        config.read("config.ini")
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}", exc_info=True)
    return config

def setup_logging():
    # Set up logging configuration
    logging.basicConfig(
        level=logging.DEBUG,  # Set the desired level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )

# Set up logging before anything else
setup_logging()
logger = logging.getLogger(__name__)
