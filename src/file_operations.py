# file_operations.py

import os
import shutil
import logging
import tkinter as tk
from tkinter import messagebox, simpledialog
from data_storage import save_data, load_data  # Ensure load_data is also imported if used
from PIL import Image, ImageTk
import defusedxml.ElementTree as ET  # Ensure defusedxml is installed


def rename_images(folder_path, author_name, status_label, app, operation_mode="Rename", destination_folder=None, progress_callback=None):
    """
    Rename, copy, or move images and save the original filenames for undo functionality.
    """
    try:
        files = sorted([
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ])

        total_files = len(files)
        if progress_callback:
            progress_callback("start", total_files)
        
        skipped_files = []
        operations = []  # List to keep track of operations

        for index, filename in enumerate(files, start=1):
            old_file = os.path.join(folder_path, filename)

            # Split the filename into name and extension
            name_part, ext_part = os.path.splitext(filename)
            ext_part = ext_part.lower()

            # Check if 'by {author_name}' is already in the filename
            author_marker = f"by {author_name}"
            if author_marker.lower() in name_part.lower():
                # Skip renaming this file
                logging.info(f"Skipping '{filename}' as it already contains 'by {author_name}'")
                skipped_files.append(filename)
                if progress_callback:
                    progress_callback("update", 1)
                continue

            base_new_name = f"{name_part} by {author_name}"
            new_name = f"{base_new_name}{ext_part}"

            # Determine the new file path
            if operation_mode in ["Copy", "Move"] and destination_folder:
                new_file = os.path.join(destination_folder, new_name)
            else:
                new_file = os.path.join(folder_path, new_name)

            # Handle duplicate filenames
            counter = 1
            while os.path.exists(new_file):
                new_name = f"{base_new_name} {counter}{ext_part}"
                if operation_mode in ["Copy", "Move"] and destination_folder:
                    new_file = os.path.join(destination_folder, new_name)
                else:
                    new_file = os.path.join(folder_path, new_name)
                counter += 1

            # Perform the selected operation
            try:
                if operation_mode == "Rename":
                    os.rename(old_file, new_file)
                    operations.append((new_file, old_file))
                    logging.info(f"Renamed '{old_file}' to '{new_file}'")
                elif operation_mode == "Copy":
                    shutil.copy2(old_file, new_file)
                    operations.append((new_file, None))  # None indicates original file is unchanged
                    logging.info(f"Copied '{old_file}' to '{new_file}'")
                elif operation_mode == "Move":
                    shutil.move(old_file, new_file)
                    operations.append((new_file, old_file))
                    logging.info(f"Moved '{old_file}' to '{new_file}'")
                else:
                    logging.error(f"Unknown operation mode: {operation_mode}")
                    continue
            except Exception as e:
                logging.error(f"Error during {operation_mode.lower()} '{old_file}' to '{new_file}': {e}")
                if progress_callback:
                    progress_callback("error", f"Error renaming '{filename}': {e}")
                continue

            # Update progress
            if progress_callback:
                progress_callback("update", 1)

        # Save the operations to the app's undo stack
        if operations:
            app.undo_stack.append((operation_mode, operations))
            app.update_undo_button_state()  # Enable the undo button

        # Provide feedback on skipped files
        if skipped_files:
            skipped_message = (
                "The following files were skipped as they already contain the author name:\n"
                + "\n".join(skipped_files)
            )
            logging.info(skipped_message)
            if progress_callback:
                progress_callback("skipped", skipped_message)

        if progress_callback:
            progress_callback("done")

    except Exception as e:
        logging.error(f"Error during {operation_mode.lower()}: {e}")
        if progress_callback:
            progress_callback("error", f"An error occurred: {e}")

def rename_images_by_folder_name(folder_path, author_name, status_label, app, operation_mode="Rename", destination_folder=None, progress_callback=None):
    """
    Rename, copy, or move images by prefixing the folder name and appending the author name.
    """
    try:
        folder_name = os.path.basename(folder_path)
        files = sorted([
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ])

        total_files = len(files)
        if progress_callback:
            progress_callback("start", total_files)

        operations = []  # List to keep track of operations

        for index, filename in enumerate(files, start=1):
            old_file = os.path.join(folder_path, filename)

            # Split the filename into name and extension
            name_part, ext_part = os.path.splitext(filename)
            ext_part = ext_part.lower()

            new_name = f"{folder_name} by {author_name} {index}{ext_part}"

            # Determine the new file path
            if operation_mode in ["Copy", "Move"] and destination_folder:
                new_file = os.path.join(destination_folder, new_name)
            else:
                new_file = os.path.join(folder_path, new_name)

            # Handle duplicate filenames
            counter = 1
            while os.path.exists(new_file):
                new_name = f"{folder_name} by {author_name} {index}_{counter}{ext_part}"
                if operation_mode in ["Copy", "Move"] and destination_folder:
                    new_file = os.path.join(destination_folder, new_name)
                else:
                    new_file = os.path.join(folder_path, new_name)
                counter += 1

            # Perform the selected operation
            try:
                if operation_mode == "Rename":
                    os.rename(old_file, new_file)
                    operations.append((new_file, old_file))
                    logging.info(f"Renamed '{old_file}' to '{new_file}'")
                elif operation_mode == "Copy":
                    shutil.copy2(old_file, new_file)
                    operations.append((new_file, None))  # None indicates original file is unchanged
                    logging.info(f"Copied '{old_file}' to '{new_file}'")
                elif operation_mode == "Move":
                    shutil.move(old_file, new_file)
                    operations.append((new_file, old_file))
                    logging.info(f"Moved '{old_file}' to '{new_file}'")
                else:
                    logging.error(f"Unknown operation mode: {operation_mode}")
                    continue
            except Exception as e:
                logging.error(f"Error during {operation_mode.lower()} '{old_file}' to '{new_file}': {e}")
                if progress_callback:
                    progress_callback("error", f"Error renaming '{filename}': {e}")
                continue

            # Update progress
            if progress_callback:
                progress_callback("update", 1)

        # Save the operations to the app's undo stack
        if operations:
            app.undo_stack.append((operation_mode, operations))
            app.update_undo_button_state()  # Enable the undo button

        if progress_callback:
            progress_callback("done")

    except Exception as e:
        logging.error(f"Error during {operation_mode.lower()} by folder name: {e}")
        if progress_callback:
            progress_callback("error", f"An error occurred: {e}")

def rename_images_by_character_name(folder_path, author_name, status_label, character_names, app, operation_mode="Rename", destination_folder=None, progress_callback=None):
    """
    Rename, copy, or move images by matching character names and adding the author name.
    """
    try:
        files = sorted([
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ])

        total_files = len(files)
        if progress_callback:
            progress_callback("start", total_files)

        operations = []  # List to keep track of operations

        for index, filename in enumerate(files, start=1):
            old_file = os.path.join(folder_path, filename)
            matched = False
            matched_word = ""

            for word in character_names:
                if word.lower() in filename.lower():
                    matched_word = word  # Preserve original capitalization
                    extension = os.path.splitext(filename)[1]
                    author_part = f' by {author_name}' if author_name else ''
                    
                    # Always append a number to the filename
                    counter = 1
                    base_new_filename = f'{matched_word}{author_part} {counter}{extension}'

                    # Determine the new file path
                    if operation_mode in ["Copy", "Move"] and destination_folder:
                        new_file = os.path.join(destination_folder, base_new_filename)
                    else:
                        new_file = os.path.join(folder_path, base_new_filename)

                    # Handle duplicate filenames
                    while os.path.exists(new_file):
                        counter += 1
                        base_new_filename = f'{matched_word}{author_part} {counter}{extension}'
                        if operation_mode in ["Copy", "Move"] and destination_folder:
                            new_file = os.path.join(destination_folder, base_new_filename)
                        else:
                            new_file = os.path.join(folder_path, base_new_filename)

                    # Perform the selected operation
                    try:
                        if operation_mode == "Rename":
                            os.rename(old_file, new_file)
                            operations.append((new_file, old_file))
                            logging.info(f"Renamed '{old_file}' to '{new_file}'")
                        elif operation_mode == "Copy":
                            shutil.copy2(old_file, new_file)
                            operations.append((new_file, None))
                            logging.info(f"Copied '{old_file}' to '{new_file}'")
                        elif operation_mode == "Move":
                            shutil.move(old_file, new_file)
                            operations.append((new_file, old_file))
                            logging.info(f"Moved '{old_file}' to '{new_file}'")
                        else:
                            logging.error(f"Unknown operation mode: {operation_mode}")
                            continue
                    except Exception as e:
                        logging.error(f"Error during {operation_mode.lower()} '{old_file}' to '{new_file}': {e}")
                        if progress_callback:
                            progress_callback("error", f"Error renaming '{filename}': {e}")
                        continue

                    matched = True
                    break  # Exit the character_names loop

            if not matched:
                # Prompt the user to add a new character name
                response = messagebox.askyesno(
                    "Add Character Name",
                    f"No character name found in '{filename}'. Do you want to add a new character name?"
                )
                if response:
                    # Suggest a default value from the filename
                    default_name = os.path.splitext(filename)[0].strip()
                    new_character_name = simpledialog.askstring(
                        "New Character Name",
                        f"Enter the new character name for '{filename}':",
                        initialvalue=default_name,
                        parent=app
                    )
                    if new_character_name:
                        # Add the new character name to the list
                        character_names.append(new_character_name)
                        character_names = sorted(character_names)
                        app.character_name_combo['values'] = character_names
                        app.data['character_names'] = character_names
                        save_data(app.DATA_FILE, app.data)
                        logging.info(f"Added new character name: {new_character_name}")
                    else:
                        logging.info(f"No character name provided for '{filename}'. Skipping file.")
                        if progress_callback:
                            progress_callback("update", 1)
                        continue

                    # Proceed to rename the file with the new character name
                    extension = os.path.splitext(filename)[1]
                    author_part = f' by {author_name}' if author_name else ''
                    
                    # Always append a number to the filename
                    counter = 1
                    base_new_filename = f'{new_character_name}{author_part} {counter}{extension}'

                    # Determine the new file path
                    if operation_mode in ["Copy", "Move"] and destination_folder:
                        new_file = os.path.join(destination_folder, base_new_filename)
                    else:
                        new_file = os.path.join(folder_path, base_new_filename)

                    # Handle duplicate filenames
                    while os.path.exists(new_file):
                        counter += 1
                        base_new_filename = f'{new_character_name}{author_part} {counter}{extension}'
                        if operation_mode in ["Copy", "Move"] and destination_folder:
                            new_file = os.path.join(destination_folder, base_new_filename)
                        else:
                            new_file = os.path.join(folder_path, base_new_filename)

                    # Perform the selected operation
                    try:
                        if operation_mode == "Rename":
                            os.rename(old_file, new_file)
                            operations.append((new_file, old_file))
                            logging.info(f"Renamed '{old_file}' to '{new_file}'")
                        elif operation_mode == "Copy":
                            shutil.copy2(old_file, new_file)
                            operations.append((new_file, None))
                            logging.info(f"Copied '{old_file}' to '{new_file}'")
                        elif operation_mode == "Move":
                            shutil.move(old_file, new_file)
                            operations.append((new_file, old_file))
                            logging.info(f"Moved '{old_file}' to '{new_file}'")
                        else:
                            logging.error(f"Unknown operation mode: {operation_mode}")
                            continue
                    except Exception as e:
                        logging.error(f"Error during {operation_mode.lower()} '{old_file}' to '{new_file}': {e}")
                        if progress_callback:
                            progress_callback("error", f"Error renaming '{filename}': {e}")
                        continue

            # Update progress
            if progress_callback:
                progress_callback("update", 1)

        # Save the operations to the app's undo stack
        if operations:
            app.undo_stack.append((operation_mode, operations))
            app.update_undo_button_state()  # Enable the undo button

        if progress_callback:
            progress_callback("done")

    except Exception as e:
        logging.error(f"Error during {operation_mode.lower()} by character name: {e}")
        if progress_callback:
            progress_callback("error", f"An error occurred: {e}")


def prompt_author_choice(folder_name, preselected_author):
    """
    Prompt the user to choose how to select the author name for renaming files.

    Args:
        folder_name (str): The name of the folder.
        preselected_author (str): The currently selected author in the UI.

    Returns:
        str: The chosen author name, or None if canceled.
    """
    options = [
        f"Use '{preselected_author}' (preselected author)",
        f"Use a word from the folder name '{folder_name}'"
    ]

    choice = simpledialog.askstring(
        "Choose Author Name",
        "Select how you want to rename the files:\n"
        "1. Use the preselected author.\n"
        f"2. Use a word from the folder name '{folder_name}'.",
    )

    if choice == "1":
        return preselected_author
    elif choice == "2":
        # Split the folder name into words and let the user select one
        folder_words = folder_name.split("_")
        selected_word = simpledialog.askstring(
            "Choose Folder Word",
            f"Available words: {', '.join(folder_words)}\nType one word to use as the author:",
        )
        if selected_word in folder_words:
            return selected_word
        else:
            messagebox.showerror("Invalid Choice", "You didn't select a valid word from the folder name.")
            return None
    else:
        messagebox.showwarning("Canceled", "Operation canceled by the user.")
        return None