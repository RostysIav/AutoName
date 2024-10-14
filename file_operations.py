# file_operations.py
import os
from tkinter import messagebox, simpledialog
import logging

# At the top of file_operations.py
undo_stack = []  # A global stack to keep track of rename operations

def rename_images(folder_path, author_name, status_label, app):
    """
    Rename images and save the original filenames for undo functionality.
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
        rename_operations = []  # List to keep track of renames in this operation

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
                new_name = f"{base_new_name} {counter}.{ext_part}"
                new_file = os.path.join(folder_path, new_name)
                counter += 1

            # Rename the file and save the operation
            os.rename(old_file, new_file)
            logging.info(f"Renamed '{old_file}' to '{new_file}'")
            rename_operations.append((new_file, old_file))  # Save new and original paths

        # Save the operations to the app's undo stack
        if rename_operations:
            app.undo_stack.append(rename_operations)
            app.update_undo_button_state()  # Enable the undo button

        # Provide feedback on skipped files
        if skipped_files:
            skipped_message = "The following files were skipped as they already contain the author name:\n" + "\n".join(skipped_files)
            messagebox.showinfo("Skipped Files", skipped_message, parent=app)
            logging.info(skipped_message)

        messagebox.showinfo("Success", "Images renamed successfully!", parent=app)
        status_label.config(text="Renaming completed.")
        logging.info("Renaming completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}", parent=app)
        status_label.config(text="An error occurred during renaming.")
        logging.error(f"Error renaming images: {e}")


def rename_images_by_folder_name(folder_path, author_name, status_label, app):
    """
    Rename images by prefixing the folder name and appending the author name.
    Records operations for undo functionality.
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

        rename_operations = []  # List to keep track of renames in this operation

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

            # Rename the file and save the operation
            os.rename(old_file, new_file)
            logging.info(f"Renamed '{old_file}' to '{new_file}'")
            rename_operations.append((new_file, old_file))  # Save new and original paths

        # Save the operations to the app's undo stack
        if rename_operations:
            app.undo_stack.append(rename_operations)
            app.update_undo_button_state()  # Enable the undo button

        messagebox.showinfo("Success", "Images renamed successfully!", parent=app)
        status_label.config(text="Renaming by folder name completed.")
        logging.info("Renaming by folder name completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}", parent=app)
        status_label.config(text="An error occurred during renaming by folder name.")
        logging.error(f"Error renaming images by folder name: {e}")


def rename_images_by_character_name(folder_path, author_name, status_label, character_names, app):
    """
    Rename images by matching character names and adding the author name.
    Records operations for undo functionality.
    """
    try:
        status_label.config(text="Renaming images by character names...")
        logging.info(f"Renaming images in {folder_path} by character names and {author_name}")

        rename_operations = []  # List to keep track of renames in this operation

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
                            rename_operations.append((new_path, old_path))  # Save new and original paths
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
                        parent=app
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
                            # Update the data file
                            if hasattr(app, 'data'):
                                app.data['character_names'] = character_names
                                from data_storage import save_data
                                save_data(app.DATA_FILE, app.data)
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
                                rename_operations.append((new_path, old_path))  # Save new and original paths
                            except Exception as e:
                                logging.error(f"Error renaming '{old_path}' to '{new_path}': {e}")
                        else:
                            logging.info(f"No character name provided for '{filename}'. Skipping file.")
                            continue
                    else:
                        logging.info(f"User declined to add a character name for '{filename}'. Skipping file.")
                        continue

        # Save the operations to the app's undo stack
        if rename_operations:
            app.undo_stack.append(rename_operations)
            app.update_undo_button_state()  # Enable the undo button

        logging.info("Renaming process completed.")
        messagebox.showinfo('Renaming Complete', 'Renaming process completed.', parent=app)
        status_label.config(text="Renaming by character names completed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}", parent=app)
        status_label.config(text="An error occurred during renaming by character names.")
        logging.error(f"Error renaming images by character names: {e}")
