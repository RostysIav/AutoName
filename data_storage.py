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

def add_author(author_name, data_file):
    """
    Add an author to the data file.

    Args:
        author_name (str): The name of the author to add.
        data_file (str): The path to the JSON data file.
    """
    data = load_data(data_file)
    authors = data.get('authors', [])
    if author_name in authors:
        logging.info(f"Author '{author_name}' already exists.")
        return False
    authors.append(author_name)
    data['authors'] = authors
    save_data(data_file, data)
    logging.info(f"Added new author: {author_name}")
    return True

# def load_authors(data_file):
#     """
#     Load authors from the JSON data file.

#     Args:
#         data_file (str): The path to the JSON data file.

#     Returns:
#         list: A list of author names.
#     """
#     data = load_data(data_file)
#     authors = data.get('authors', [])
#     logging.info(f"Loaded authors from {data_file}")
#     return authors

# def save_authors(authors, data_file):
#     """
#     Save authors to the JSON data file.

#     Args:
#         authors (list): A list of author names.
#         data_file (str): The path to the JSON data file.
#     """
#     data = load_data(data_file)
#     data['authors'] = authors
#     save_data(data_file, data)
#     logging.info(f"Saved authors to {data_file}")

def add_character_name(character_name, data_file):
    data = load_data(data_file)
    character_names = data.get('character_names', [])
    if character_name in character_names:
        logging.info(f"Character name '{character_name}' already exists.")
        return False
    character_names.append(character_name)
    data['character_names'] = character_names
    save_data(data_file, data)
    logging.info(f"Added new character name: {character_name}")
    return True
