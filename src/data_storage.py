import os
import json
import logging

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
DATA_FILE = os.path.join(DATA_DIR, "data.json")
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

def load_data(filename=DATA_FILE):
    """
    Load data from a JSON file.

    Args:
        filename (str): Path to the JSON file.

    Returns:
        dict: A dictionary containing the data.
    """
    if not os.path.exists(filename):
        # Create an empty JSON file if it doesn't exist
        logging.info(f"{filename} does not exist. Creating a new file.")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"authors": [], "character_names": []}, f, indent=4)

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {filename}: {e}")
        return {"authors": [], "character_names": []}
    except Exception as e:
        logging.error(f"Error loading data from {filename}: {e}")
        return {"authors": [], "character_names": []}

def save_data(filename=DATA_FILE, data=None):
    """
    Save data to a JSON file.

    Args:
        filename (str): Path to the JSON file.
        data (dict): The data to save.
    """
    if data is None:
        data = {"authors": [], "character_names": []}

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")

def add_author(author_name, data_file=DATA_FILE):
    """
    Add an author to the data file.

    Args:
        author_name (str): The name of the author to add.
        data_file (str): The path to the JSON data file.

    Returns:
        bool: True if added successfully, False otherwise.
    """
    data = load_data(data_file)
    if 'authors' not in data:
        data['authors'] = []
    if author_name not in data['authors']:
        data['authors'].append(author_name)
        save_data(data_file, data)
        logging.info(f"Added new author: {author_name}")
        return True
    else:
        logging.info(f"Author '{author_name}' already exists.")
        return False

def add_character_name(character_name, data_file=DATA_FILE):
    """
    Add a character name to the data file.

    Args:
        character_name (str): The name of the character to add.
        data_file (str): The path to the JSON data file.

    Returns:
        bool: True if added successfully, False otherwise.
    """
    data = load_data(data_file)
    if 'character_names' not in data:
        data['character_names'] = []
    if character_name not in data['character_names']:
        data['character_names'].append(character_name)
        save_data(data_file, data)
        logging.info(f"Added new character name: {character_name}")
        return True
    else:
        logging.info(f"Character name '{character_name}' already exists.")
        return False

def delete_author(author_name, data_file=DATA_FILE):
    """
    Delete an author from the data file.

    Args:
        author_name (str): The name of the author to delete.
        data_file (str): The path to the JSON data file.

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    data = load_data(data_file)
    if 'authors' in data and author_name in data['authors']:
        data['authors'].remove(author_name)
        save_data(data_file, data)
        logging.info(f"Deleted author: {author_name}")
        return True
    else:
        logging.info(f"Author '{author_name}' does not exist.")
        return False

def delete_character_name(character_name, data_file=DATA_FILE):
    """
    Delete a character name from the data file.

    Args:
        character_name (str): The name of the character to delete.
        data_file (str): The path to the JSON data file.

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    data = load_data(data_file)
    if 'character_names' in data and character_name in data['character_names']:
        data['character_names'].remove(character_name)
        save_data(data_file, data)
        logging.info(f"Deleted character name: {character_name}")
        return True
    else:
        logging.info(f"Character name '{character_name}' does not exist.")
        return False
