import os
import logging
import configparser
from gui import App

# Set directory paths at the top of the file so they are accessible globally
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# File paths
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")
AUTHOR_FILE = os.path.join(CONFIG_DIR, "authors.txt")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logging.info("Logging is set up.")

# Read or create configuration
config = configparser.ConfigParser()
if not os.path.exists(CONFIG_FILE):
    # Create default config if it doesn't exist
    config['DEFAULT'] = {
        'AuthorFile': AUTHOR_FILE,
        'LogFile': LOG_FILE,
        'LastAuthor': ''
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    logging.info("Default config file created.")
else:
    config.read(CONFIG_FILE)
    logging.info("Config file loaded.")

# Access configurations
AUTHOR_FILE = config['DEFAULT'].get('AuthorFile', AUTHOR_FILE)
LOG_FILE = config['DEFAULT'].get('LogFile', LOG_FILE)

# Import and run the GUI application
if __name__ == "__main__":
    logging.info("Starting the application...")
    app = App()
    app.mainloop()
