# data_storage.py
import os
import json
import logging

def load_data(filename):
    """
    Load data from a JSON file.

    Args:
        filename (str): Path to the JSON file.

    Returns:
        dict: A dictionary containing the data.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        # If the file doesn't exist, return empty data
        logging.warning(f"Data file {filename} not found. Using empty data.")
        return {"authors": [], "character_names": []}
    except Exception as e:
        logging.error(f"Error loading data from {filename}: {e}")
        return {"authors": [], "character_names": []}

def save_data(filename, data):
    """
    Save data to a JSON file.

    Args:
        filename (str): Path to the JSON file.
        data (dict): The data to save.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")
        
def load_authors(author_file):
    """
    Load authors from the specified file.

    Args:
        author_file (str): The path to the author file.

    Returns:
        list: A list of author names.
    """
    try:
        if os.path.exists(author_file):
            with open(author_file, 'r') as file:
                authors = [line.strip() for line in file.readlines()]
                logging.info(f"Loaded authors from {author_file}")
                return authors
        else:
            logging.info(f"No author file found at {author_file}. Starting with an empty list.")
            return []
    except Exception as e:
        logging.error(f"Error loading authors: {e}")
        return []

def save_authors(authors, author_file):
    """
    Save authors to the specified file.

    Args:
        authors (list): A list of author names.
        author_file (str): The path to the author file.
    """
    try:
        with open(author_file, 'w') as file:
            file.write('\n'.join(authors))
        logging.info(f"Saved authors to {author_file}")
    except Exception as e:
        logging.error(f"Error saving authors: {e}")
