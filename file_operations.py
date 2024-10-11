# file_operations.py
import os
from tkinter import messagebox
import logging

# file_operations.py

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

def rename_images_by_character_name(folder_path, author_name, status_label, words_to_match):
    """
    Rename images by matching character names and adding the author name.

    Args:
        folder_path (str): The path to the folder containing images.
        author_name (str): The author's name to append.
        status_label (tk.Label): The status label to update the status.
        words_to_match (list): List of character names to match in filenames.
    """
    try:
        status_label.config(text="Renaming images by character names...")
        logging.info(f"Renaming images in {folder_path} by character names and {author_name}")

        unmatched_files = []

        for root_dir, dirs, files in os.walk(folder_path):
            for filename in files:
                matched = False
                for word in words_to_match:
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
                            # Modify here to append counter without parentheses
                            name_without_ext = os.path.splitext(base_new_filename)[0]
                            new_filename = f'{name_without_ext} {counter}{extension}'
                            new_path = os.path.join(root_dir, new_filename)
                            counter += 1

                        try:
                            os.rename(old_path, new_path)
                            logging.info(f"Renamed '{old_path}' to '{new_path}'")
                            matched = True
                            break
                        except Exception as e:
                            logging.error(f"Error renaming '{old_path}' to '{new_path}': {e}")
                            unmatched_files.append(f"{filename} (Error: {e})")
                            matched = True  # Consider it matched even if there's an error
                            break
                if not matched:
                    # If no match is found, add the file to unmatched_files
                    relative_path = os.path.relpath(os.path.join(root_dir, filename), folder_path)
                    unmatched_files.append(relative_path)

        if unmatched_files:
            message = 'Some files could not be renamed because no matching character names were found or an error occurred:\n\n' + '\n'.join(unmatched_files)
            logging.info(message)
            messagebox.showinfo('Renaming Complete with Unmatched Files', message)
        else:
            logging.info("All files were renamed successfully.")
            messagebox.showinfo('Renaming Complete', 'All files were renamed successfully.')

        status_label.config(text="Renaming by character names completed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        status_label.config(text="An error occurred during renaming by character names.")
        logging.error(f"Error renaming images by character names: {e}")
