# main.py
from gui import App
import logging
# main.py or gui.py
import configparser
# Configure logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Access configurations
AUTHOR_FILE = config['DEFAULT'].get('AuthorFile', 'authors.txt')
LOG_FILE = config['DEFAULT'].get('LogFile', 'app.log')


if __name__ == "__main__":
    app = App()
    app.mainloop()
