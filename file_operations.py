# file_operations.py
import os
from tkinter import messagebox, simpledialog
import logging

def rename_images(folder_path, author_name, status_label):
    """
    Rename images in the specified folder by appending 'by {author_name}'.
    Checks if 'by {author_name}' is already present to avoid duplication.
    Handles duplicate filenames by appending a number at the end.
    """
    try:
        status_label.config(text="Renaming images...")
        logging.info(f"Renaming images in {folder_path} by {author_name}")

        # Capture and sort the list of image files
        files = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
        ])

        skipped_files = []

        for filename in files:
            old_file = os.path.join(folder_path, filename)

            # Split the filename into name and extension
            if '.' in filename:
                name_part, ext_part = filename.rsplit('.', 1)
                ext_part = ext_part.lower()
            else:
                name_part = filename
                ext_part = ''

            # Check if 'by {author_name}' is already in the filename
            author_marker = f"by {author_name}"
            if author_marker.lower() in name_part.lower():
                # Skip renaming this file
                logging.info(f"Skipping '{filename}' as it already contains 'by {author_name}'")
                skipped_files.append(filename)
                continue

            base_new_name = f"{name_part} by {author_name}"
            new_name = f"{base_new_name}.{ext_part}"
            new_file = os.path.join(folder_path, new_name)

            # Handle duplicate filenames
            counter = 1
            while os.path.exists(new_file):
                # Append the counter without parentheses
                new_name = f"{base_new_name} {counter}.{ext_part}"
                new_file = os.path.join(folder_path, new_name)
                counter += 1

            # Rename the file
            os.rename(old_file, new_file)
            logging.info(f"Renamed '{old_file}' to '{new_file}'")

        # Provide feedback on skipped files
        if skipped_files:
            skipped_message = "The following files were skipped as they already contain the author name:\n" + "\n".join(skipped_files)
            messagebox.showinfo("Skipped Files", skipped_message)
            logging.info(skipped_message)

        messagebox.showinfo("Success", "Images renamed successfully!")
        status_label.config(text="Renaming completed.")
        logging.info("Renaming completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        status_label.config(text="An error occurred during renaming.")
        logging.error(f"Error renaming images: {e}")


def rename_images_by_folder_name(folder_path, author_name, status_label):
    """
    Rename images by prefixing the folder name and appending the author name.
    """
    try:
        status_label.config(text="Renaming images by folder name...")
        logging.info(f"Renaming images in {folder_path} by folder name and {author_name}")
        folder_name = os.path.basename(folder_path)

        # Capture and sort the list of image files
        files = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
        ])

        for count, filename in enumerate(files, start=1):
            old_file = os.path.join(folder_path, filename)

            # Split the filename into name and extension
            if '.' in filename:
                _, ext_part = filename.rsplit('.', 1)
                ext_part = ext_part.lower()
            else:
                ext_part = ''

            new_name = f"{folder_name} by {author_name} {count}.{ext_part}"
            new_file = os.path.join(folder_path, new_name)
            os.rename(old_file, new_file)

        messagebox.showinfo("Success", "Images renamed successfully!")
        status_label.config(text="Renaming by folder name completed.")
        logging.info("Renaming by folder name completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        status_label.config(text="An error occurred during renaming by folder name.")
        logging.error(f"Error renaming images by folder name: {e}")


def rename_images_by_character_name(folder_path, author_name, status_label, character_names, self):
    """
    Rename images by matching character names and adding the author name.
    If no character name is found, prompt the user to add a new character name.

    Args:
        folder_path (str): The path to the folder containing images.
        author_name (str): The author's name to append.
        status_label (tk.Label): The status label to update the status.
        character_names (list): List of character names to match in filenames.
        app (App): The main application instance.
    """
    try:
        status_label.config(text="Renaming images by character names...")
        logging.info(f"Renaming images in {folder_path} by character names and {author_name}")

        for root_dir, dirs, files in os.walk(folder_path):
            for filename in files:
                matched = False
                for word in character_names:
                    if word.lower() in filename.lower():
                        matched_word = word  # Preserve original capitalization
                        extension = os.path.splitext(filename)[1]
                        author_part = f' by {author_name}' if author_name else ''
                        base_new_filename = f'{matched_word}{author_part}{extension}'

                        old_path = os.path.join(root_dir, filename)
                        new_filename = base_new_filename
                        new_path = os.path.join(root_dir, new_filename)

                        # Handle duplicate filenames
                        counter = 1
                        while os.path.exists(new_path):
                            name_without_ext = os.path.splitext(base_new_filename)[0]
                            new_filename = f'{name_without_ext} {counter}{extension}'
                            new_path = os.path.join(root_dir, new_filename)
                            counter += 1

                        try:
                            os.rename(old_path, new_path)
                            logging.info(f"Renamed '{old_path}' to '{new_path}'")
                            matched = True
                            break  # Exit the character_names loop
                        except Exception as e:
                            logging.error(f"Error renaming '{old_path}' to '{new_path}': {e}")
                            matched = True  # Consider it matched even if there's an error
                            break

                if not matched:
                    # Use 'app' as the parent for dialogs
                    response = messagebox.askyesno(
                        "Add Character Name",
                        f"No character name found in '{filename}'. Do you want to add a new character name?",
                        parent=self  # Use 'app' here
                    )
                    if response:
                        # Suggest a default value from the filename
                        default_name = os.path.splitext(filename)[0].strip()
                        new_character_name = simpledialog.askstring(
                            "New Character Name",
                            f"Enter the new character name for '{filename}':",
                            initialvalue=default_name,
                            parent=self  # Use 'app' here
                        )
                        if new_character_name:
                            # Add the new character name to the list
                            character_names.append(new_character_name)
                            # Update the data file
                            if hasattr(self, 'data'):
                                self.data['character_names'] = character_names
                                from data_storage import save_data
                                save_data(self.DATA_FILE, self.data)
                                logging.info(f"Added new character name: {new_character_name}")
                            else:
                                logging.warning("Unable to save new character name to data file.")

                            # Proceed to rename the file with the new character name
                            matched_word = new_character_name
                            extension = os.path.splitext(filename)[1]
                            author_part = f' by {author_name}' if author_name else ''
                            base_new_filename = f'{matched_word}{author_part}{extension}'

                            old_path = os.path.join(root_dir, filename)
                            new_filename = base_new_filename
                            new_path = os.path.join(root_dir, new_filename)

                            # Handle duplicate filenames
                            counter = 1
                            while os.path.exists(new_path):
                                name_without_ext = os.path.splitext(base_new_filename)[0]
                                new_filename = f'{name_without_ext} {counter}{extension}'
                                new_path = os.path.join(root_dir, new_filename)
                                counter += 1

                            try:
                                os.rename(old_path, new_path)
                                logging.info(f"Renamed '{old_path}' to '{new_path}'")
                            except Exception as e:
                                logging.error(f"Error renaming '{old_path}' to '{new_path}': {e}")
                        else:
                            logging.info(f"No character name provided for '{filename}'. Skipping file.")
                            continue
                    else:
                        logging.info(f"User declined to add a character name for '{filename}'. Skipping file.")
                        continue

        logging.info("Renaming process completed.")
        messagebox.showinfo('Renaming Complete', 'Renaming process completed.')
        status_label.config(text="Renaming by character names completed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        status_label.config(text="An error occurred during renaming by character names.")
        logging.error(f"Error renaming images by character names: {e}")
