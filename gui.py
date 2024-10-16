# gui.py

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import configparser
from file_operations import rename_images, rename_images_by_folder_name, rename_images_by_character_name
from data_storage import load_data, save_data, add_author, delete_author, add_character_name, delete_character_name
from logging.handlers import QueueHandler
import queue
from PIL import Image, ImageTk 
import shutil 


# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

DATA_FILE = config['DEFAULT'].get('DataFile', 'data.json')
LOG_FILE = config['DEFAULT'].get('LogFile', 'app.log')

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)  # Set root logger level

# Remove any existing handlers
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# Create a FileHandler to write logs to the file
file_handler = logging.FileHandler(LOG_FILE, mode='a')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

class App(tk.Tk):
    """Main application class for the Image Renamer."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.title("Image Renamer")
        self.geometry("1400x600")

        # Undo operations
        self.undo_stack = []  # Stack to keep track of undo operations

        # Load data from JSON file
        # Add DATA_FILE + LOG_FILE as an attribute
        self.DATA_FILE = DATA_FILE
        self.LOG_FILE = LOG_FILE
        self.data = load_data(DATA_FILE)
        self.authors = self.data.get('authors', [])
        self.character_names = self.data.get('character_names', [])

        # Create GUI components
        self.create_left_menu()
        self.create_right_menu()
        self.create_main_frame()
        self.create_status_bar()
        self.create_log_window()
        self.create_undo_button() 
        self.setup_logging()

        # Load the last used author
        self.load_last_author()

        # Bind the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.operation_mode = tk.StringVar(value="Rename")  # Default operation mode
        self.create_operation_mode_selector()


    def create_left_menu(self):
        """Create the left menu with Exit and Restart buttons."""
        self.left_frame = tk.Frame(self, width=200, bg='lightgrey')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.exit_button = tk.Button(self.left_frame, text="Exit", command=self.exit_app, width=15)
        self.exit_button.pack(pady=20)

        self.restart_button = tk.Button(self.left_frame, text="Restart", command=self.restart_app, width=15)
        self.restart_button.pack(pady=20)

    def create_right_menu(self):
        # Author section
        """Create the right menu for author selection."""
        self.right_frame = tk.Frame(self, width=200, bg='lightgrey')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.author_label = tk.Label(self.right_frame, text="Author Name")
        self.author_label.pack(pady=10)

        self.author_combo = ttk.Combobox(self.right_frame, values=self.authors)
        self.author_combo.pack(pady=5)
        self.author_combo.focus()

        self.author_entry = tk.Entry(self.right_frame)
        self.author_entry.pack(pady=5)

        self.add_author_button = tk.Button(
            self.right_frame, text="Add Author", command=self.add_author
        )
        self.add_author_button.pack(pady=5)

        self.delete_author_button = tk.Button(
            self.right_frame, text="Delete Author", command=self.delete_author
        )
        self.delete_author_button.pack(pady=5)

        # Undo Delete Button
        self.undo_delete_button = tk.Button(
            self.right_frame, text="Undo Delete", command=self.undo_last_deletion
        )
        self.undo_delete_button.pack(pady=5)

        # Character name section
        self.character_name_label = tk.Label(self.right_frame, text="Character Name")
        self.character_name_label.pack(pady=10)

        self.character_name_combo = ttk.Combobox(self.right_frame, values=self.character_names)
        self.character_name_combo.pack(pady=5)
        self.character_name_combo.focus()

        self.character_name_entry = tk.Entry(self.right_frame)
        self.character_name_entry.pack(pady=5)

        self.add_character_name_button = tk.Button(
            self.right_frame, text="Add Character", command=self.add_character_name
        )
        self.add_character_name_button.pack(pady=5)

        self.delete_character_name_button = tk.Button(
            self.right_frame, text="Delete Character", command=self.delete_character_name
        )
        self.delete_character_name_button.pack(pady=5)

        # Undo Delete Button
        self.undo_delete_button = tk.Button(
            self.right_frame, text="Undo Delete", command=self.undo_last_deletion
        )
        self.undo_delete_button.pack(pady=5)

    def create_main_frame(self):
        """Create the main frame containing the directory entry and tree view."""
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Entry and Go button frame
        self.entry_frame = tk.Frame(self.main_frame)
        self.entry_frame.pack(fill=tk.X, pady=5)

        self.path_entry = tk.Entry(self.entry_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.go_button = tk.Button(self.entry_frame, text="Go", command=self.load_path)
        self.go_button.pack(side=tk.LEFT, padx=5)

        # Tree view frame
        self.tree_frame = tk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree = ttk.Treeview(self.tree_frame, columns=("abspath",), displaycolumns=())
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.heading("#0", text="Directory Structure", anchor='w')

        # Populate drives
        drive_nodes = self.get_drives()
        for drive in drive_nodes:
            self.insert_node('', drive, drive)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Rename Images", command=self.context_rename_images)
        self.context_menu.add_command(label="Rename Images by Folder Name", command=self.context_rename_images_by_folder_name)
        self.context_menu.add_command(label="Rename Images by Character Name", command=self.context_rename_images_by_character_name)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)   


    def create_status_bar(self):
        """Create the status bar at the bottom of the application."""
        self.status_label = tk.Label(self, text="Status: Ready", anchor='w', bg='lightgrey')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_log_window(self):
        """Create a collapsible frame for displaying logs."""
        self.log_frame_visible = False  # Flag to track visibility

        # Button to toggle log window
        self.toggle_log_button = tk.Button(self, text="Show Logs", command=self.toggle_log_window)
        self.toggle_log_button.pack(side=tk.BOTTOM, fill=tk.X)

        # Frame for logs (initially hidden)
        self.log_frame = tk.Frame(self)
        self.log_text = tk.Text(self.log_frame, height=10, state='disabled')
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for the log text widget
        self.log_scrollbar = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = self.log_scrollbar.set    

    def create_preview_pane(self):
        """Create a pane to display image thumbnails."""
        self.preview_frame = tk.Frame(self.main_frame, width=200, bg='white')
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.preview_label = tk.Label(self.preview_frame, text="Preview")
        self.preview_label.pack()

        self.image_label = tk.Label(self.preview_frame)
        self.image_label.pack(pady=10)  

    def create_operation_mode_selector(self):
        """Create operation mode selector (Rename, Copy, Move)."""
        self.operation_frame = tk.Frame(self.right_frame)
        self.operation_frame.pack(pady=10)

        self.operation_label = tk.Label(self.operation_frame, text="Operation Mode:")
        self.operation_label.pack(side=tk.LEFT)

        self.rename_radio = tk.Radiobutton(
            self.operation_frame, text="Rename", variable=self.operation_mode, value="Rename"
        )
        self.rename_radio.pack(side=tk.LEFT)

        self.copy_radio = tk.Radiobutton(
            self.operation_frame, text="Copy", variable=self.operation_mode, value="Copy"
        )
        self.copy_radio.pack(side=tk.LEFT)

        self.move_radio = tk.Radiobutton(
            self.operation_frame, text="Move", variable=self.operation_mode, value="Move"
        )
        self.move_radio.pack(side=tk.LEFT)

    def create_undo_button(self):
        """Create the Undo button and place it in the status bar or toolbar."""
        self.undo_button = tk.Button(self.status_label, text="Undo", command=self.undo_last_action)
        self.undo_button.pack(side=tk.RIGHT, padx=5)
        self.update_undo_button_state()  # Set initial state

    def update_undo_button_state(self):
        """Enable or disable the Undo button based on the undo stack."""
        if self.undo_stack:
            self.undo_button.config(state=tk.NORMAL)
        else:
            self.undo_button.config(state=tk.DISABLED)
    
    def undo_last_deletion(self):
        """Undo the last deletion of an author or character name."""
        if self.undo_stack:
            last_action = self.undo_stack.pop()
            action_type, name = last_action
            if action_type == 'author':
                self.authors.append(name)
                self.authors = sorted(self.authors)
                self.author_combo['values'] = self.authors
                self.data['authors'] = self.authors
                save_data(DATA_FILE, self.data)
                logging.info(f"Restored author: {name}")
                messagebox.showinfo("Undo Successful", f"Author '{name}' has been restored.")
            elif action_type == 'character':
                self.character_names.append(name)
                self.character_names = sorted(self.character_names)
                self.character_name_combo['values'] = self.character_names
                self.data['character_names'] = self.character_names
                save_data(DATA_FILE, self.data)
                logging.info(f"Restored character name: {name}")
                messagebox.showinfo("Undo Successful", f"Character '{name}' has been restored.")
        else:
            messagebox.showinfo("Nothing to Undo", "There is no deletion to undo.")

    def undo_last_action(self):
        """Undo the last renaming, copying, or moving operation."""
        if self.undo_stack:
            last_operation = self.undo_stack.pop()
            operation_mode, operations = last_operation
            errors = []

            for new_file, original_file in reversed(operations):
                try:
                    if operation_mode == "Rename":
                        os.rename(new_file, original_file)
                        logging.info(f"Reverted '{new_file}' to '{original_file}'")
                    elif operation_mode == "Copy":
                        os.remove(new_file)
                        logging.info(f"Removed copied file '{new_file}'")
                    elif operation_mode == "Move":
                        shutil.move(new_file, original_file)
                        logging.info(f"Moved '{new_file}' back to '{original_file}'")
                    else:
                        logging.error(f"Unknown operation mode: {operation_mode}")
                except Exception as e:
                    errors.append(f"Error undoing '{new_file}': {e}")
                    logging.error(f"Error undoing '{new_file}': {e}")

            if errors:
                messagebox.showerror("Undo Errors", "\n".join(errors), parent=self)
            else:
                messagebox.showinfo("Undo Successful", "Last operation has been undone.", parent=self)
            self.update_undo_button_state()
        else:
            messagebox.showinfo("No Action to Undo", "There is no action to undo.", parent=self)

    def on_tree_select(self, event):
        """Handle the event when a tree item is selected."""
        item = self.tree.selection()[0]
        abspath = self.tree.set(item, "abspath")
        if os.path.isfile(abspath):
            self.show_image_preview(abspath)
        else:
            # Clear the preview if a directory is selected
            self.image_label.config(image='')
            self.image_label.image = None

    def show_image_preview(self, image_path):
        """Display a thumbnail of the selected image."""
        try:
            img = Image.open(image_path)
            img.thumbnail((200, 200))  # Adjust the size as needed
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            logging.error(f"Error loading image '{image_path}': {e}")
            self.image_label.config(image='')
            self.image_label.image = None

    def toggle_log_window(self):
        """Toggle the visibility of the log window."""
        if self.log_frame_visible:
            self.log_frame.pack_forget()
            self.toggle_log_button.config(text="Show Logs")
            self.log_frame_visible = False
        else:
            self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
            self.toggle_log_button.config(text="Hide Logs")
            self.log_frame_visible = True   

    def setup_logging(self):
        """Set up logging to display log messages in the GUI."""
        # Create a queue to hold log records
        self.log_queue = queue.Queue()

        # Create a handler that writes to the queue
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        root_logger.addHandler(queue_handler)

        # Create a formatter for log messages in the GUI
        self.gui_log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Initialize the polling flag
        self.polling = True    
        # Start polling the queue
        self.poll_log_queue()

    def append_log_message(self, msg):
        """Append a log message to the log text widget."""
        try:
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, msg + '\n')
            self.log_text.configure(state='disabled')
            # Auto-scroll to the end
            self.log_text.yview(tk.END)
        except Exception as e:
            logging.error(f"Error appending log message: {e}")


    def format_log_record(self, record):
        """Format the log record for display."""
        return self.gui_log_formatter.format(record)

    def poll_log_queue(self):
        """Check for new log messages in the queue and display them."""
        if self.polling:
            while not self.log_queue.empty():
                record = self.log_queue.get()
                msg = self.gui_log_formatter.format(record)
                self.append_log_message(msg)
            # Store the after ID
            self.after_id = self.after(100, self.poll_log_queue)
   
    def add_author(self):
        """Add a new author to the list."""
        author_name = self.author_entry.get().strip()
        if author_name and author_name not in self.authors:
            success = add_author(author_name, DATA_FILE)
            if success:
                self.authors.append(author_name)
                self.authors = sorted(self.authors)
                self.author_combo['values'] = self.authors
                logging.info(f"Added author: {author_name}")
                messagebox.showinfo("Author Added", f"Author '{author_name}' has been added.")
            else:
                logging.error(f"Failed to add author: {author_name}")
                messagebox.showerror("Error", f"Failed to add author '{author_name}'.")
        else:
            messagebox.showerror("Error", "Please enter a valid author name to add.")

    def add_character_name(self):
        """Add a new character name to the list."""
        character_name = self.character_name_entry.get().strip()
        if character_name and character_name not in self.character_names:
            success = add_character_name(character_name, DATA_FILE)
            if success:
                self.character_names.append(character_name)
                self.character_names = sorted(self.character_names)
                self.character_name_combo['values'] = self.character_names
                logging.info(f"Added character name: {character_name}")
                messagebox.showinfo("Character Added", f"Character '{character_name}' has been added.")
            else:
                logging.error(f"Failed to add character name: {character_name}")
                messagebox.showerror("Error", f"Failed to add character name '{character_name}'.")
        else:
            messagebox.showerror("Error", "Please enter a valid character name to add.")

    def delete_author(self):
        """Delete the selected author from the list."""
        author_name = self.author_combo.get().strip()
        if author_name and author_name in self.authors:
            success = delete_author(author_name, DATA_FILE)
            if success:
                self.undo_stack.append(('author', author_name))
                self.authors.remove(author_name)
                self.authors = sorted(self.authors)
                self.author_combo['values'] = self.authors
                self.author_combo.set('')
                logging.info(f"Deleted author: {author_name}")
                messagebox.showinfo("Author Deleted", f"Author '{author_name}' has been deleted.")
            else:
                logging.error(f"Failed to delete author: {author_name}")
                messagebox.showerror("Error", f"Failed to delete author '{author_name}'.")
        else:
            messagebox.showerror("Error", "Please select a valid author to delete.")

    def delete_character_name(self):
        """Delete the selected character name from the list."""
        character_name = self.character_name_combo.get().strip()
        if character_name and character_name in self.character_names:
            success = delete_character_name(character_name, DATA_FILE)
            if success:
                self.undo_stack.append(('character', character_name))
                self.character_names.remove(character_name)
                self.character_names = sorted(self.character_names)
                self.character_name_combo['values'] = self.character_names
                self.character_name_combo.set('')
                logging.info(f"Deleted character name: {character_name}")
                messagebox.showinfo("Character Name Deleted", f"Character '{character_name}' has been deleted.")
            else:
                logging.error(f"Failed to delete character name: {character_name}")
                messagebox.showerror("Error", f"Failed to delete character name '{character_name}'.")
        else:
            messagebox.showerror("Error", "Please select a valid character name to delete.")

    def get_author_name(self):
        """
        Get the author name from the combo box.
        Returns:
            str: The selected author name.
        """
        author_name = self.author_combo.get()
        if author_name:
            if author_name not in self.authors:
                # Prompt the user to confirm adding the new author
                response = messagebox.askyesno(
                    "Add Author",
                    f"Author '{author_name}' not found. Would you like to add it?"
                )
                if response:
                    self.authors.append(author_name)
                    self.author_combo['values'] = self.authors
                    self.data['authors'] = self.authors
                    save_data(DATA_FILE, self.data)
                    logging.info(f"Added new author: {author_name}")
                    self.save_last_author(author_name)
                else:
                    logging.info(f"Author '{author_name}' not added.")
                    return None  # Return None if the user doesn't want to add the author
            else:
                self.save_last_author(author_name)
        else:
            logging.info("No author selected.")
            return None
        return author_name
    
    def save_last_author(self, author_name):
        """Save the last used author to the config file."""
        try:
            config['DEFAULT']['LastAuthor'] = author_name
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            logging.info(f"Saved last author to config: {author_name}")
        except Exception as e:
            logging.error(f"Error saving last author to config: {e}")    

    def load_last_author(self):
        """Load the last used author from the config file."""
        try:
            author_name = config['DEFAULT'].get('LastAuthor', '').strip()
            if author_name:
                if author_name not in self.authors:
                    self.authors.append(author_name)
                    self.author_combo['values'] = self.authors
                    self.data['authors'] = self.authors
                    save_data(DATA_FILE, self.data)
                self.author_combo.set(author_name)
                logging.info(f"Loaded last author from config: {author_name}")
        except Exception as e:
            logging.error(f"Error loading last author from config: {e}")    

    def get_drives(self):
        """Get the list of drives on the system."""
        drives = []
        if os.name == 'nt':
            import string
            drives = [f"{d}:/" for d in string.ascii_uppercase if os.path.exists(f"{d}:/")]
        else:
            drives = ['/']
        return drives

    def insert_node(self, parent, text, abspath):
        """Insert a node into the tree view."""
        node = self.tree.insert(parent, 'end', text=text, open=False)
        self.tree.set(node, "abspath", abspath)
        # Insert a dummy child to make the node expandable
        self.tree.insert(node, 'end')

    def on_open_node(self, event):
        """Handle the event when a node is opened."""
        node = self.tree.focus()
        abspath = self.tree.set(node, "abspath")

        # Remove the dummy node if present
        self.tree.delete(*self.tree.get_children(node))

        try:
            for p in sorted(os.listdir(abspath)):
                child_path = os.path.join(abspath, p)
                if os.path.isdir(child_path):
                    self.insert_node(node, p, child_path)
                elif child_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    # Insert image files into the tree
                    self.insert_node(node, p, child_path)
        except (PermissionError, FileNotFoundError, OSError) as e:
            logging.error(f"Error accessing {abspath}: {e}")

    def prompt_author_name_and_rename(self, folder_path, by_folder_name=False):
        """
        Prompt for the author name and perform the renaming or copying/moving.
        """
        author_name = self.get_author_name()
        if author_name:
            operation_mode = self.operation_mode.get()
            destination_folder = None

            if operation_mode in ["Copy", "Move"]:
                destination_folder = filedialog.askdirectory(title="Select Destination Folder", parent=self)
                if not destination_folder:
                    messagebox.showwarning("No Destination Selected", "Operation canceled. No destination folder selected.", parent=self)
                    return

            if by_folder_name:
                rename_images_by_folder_name(
                    folder_path, author_name, self.status_label, self, operation_mode, destination_folder
                )
            else:
                rename_images(
                    folder_path, author_name, self.status_label, self, operation_mode, destination_folder
                )

    def on_double_click(self, event):
        """Handle double-click event on a tree node."""
        item = self.tree.selection()[0]
        abspath = self.tree.set(item, "abspath")
        if os.path.isdir(abspath):
            logging.info(f"Double-clicked on directory: {abspath}")
            self.prompt_author_name_and_rename(abspath)

    def show_context_menu(self, event):
        """Show the context menu on right-click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def context_rename_images(self):
        """Context menu action to rename images."""
        item = self.tree.selection()[0]
        abspath = self.tree.set(item, "abspath")
        if os.path.isdir(abspath):
            self.prompt_author_name_and_rename(abspath)

    def context_rename_images_by_folder_name(self):
        """Context menu action to rename images by folder name."""
        item = self.tree.selection()[0]
        abspath = self.tree.set(item, "abspath")
        if os.path.isdir(abspath):
            author_name = self.get_author_name()
            if author_name:
                rename_images_by_folder_name(
                    abspath, author_name, self.status_label, self  # Pass 'self' as 'app'
                )

    def context_rename_images_by_character_name(self):
        """Context menu action to rename images by character names."""
        item = self.tree.selection()[0]
        abspath = self.tree.set(item, "abspath")
        if os.path.isdir(abspath):
            author_name = self.get_author_name()
            if author_name:
                operation_mode = self.operation_mode.get()
                destination_folder = None

                if operation_mode in ["Copy", "Move"]:
                    destination_folder = filedialog.askdirectory(title="Select Destination Folder", parent=self)
                    if not destination_folder:
                        messagebox.showwarning("No Destination Selected", "Operation canceled. No destination folder selected.", parent=self)
                        return

                rename_images_by_character_name(
                    abspath, author_name, self.status_label, self.character_names, self, operation_mode, destination_folder
                )

    def load_path(self):
        """Load the path entered in the path entry."""
        path = self.path_entry.get()
        if os.path.isdir(path):
            self.tree.delete(*self.tree.get_children())
            self.insert_node('', os.path.basename(path), path)
            self.populate_tree('', path)
            self.status_label.config(text=f"Loaded path: {path}")
            logging.info(f"Loaded path: {path}")
        else:
            messagebox.showerror("Error", "Invalid directory path")
            self.status_label.config(text="Invalid directory path")
            logging.error(f"Invalid directory path entered: {path}")

    def populate_tree(self, parent, path):
        """Populate the tree view with directories."""
        try:
            for p in sorted(os.listdir(path)):
                abspath = os.path.join(path, p)
                if os.path.isdir(abspath):
                    node = self.tree.insert(parent, 'end', text=p, open=False)
                    self.tree.set(node, "abspath", abspath)
                    # Insert a dummy child to make the node expandable
                    self.tree.insert(node, 'end')
        except (PermissionError, FileNotFoundError, OSError) as e:
            # Log the exception
            logging.error(f"Error accessing {path}: {e}")

    def exit_app(self):
        """Exit the application."""
        logging.info("Exiting application via Exit button.")
        # Save the current author to config
        author_name = self.author_combo.get()
        if author_name:
            self.save_last_author(author_name)
        else:
            logging.info("No author selected to save.")
        self.destroy()
      
    def restart_app(self):
        """Restart the application."""
        logging.info("Restarting application.")
        author_name = self.author_combo.get()
        if author_name:
            self.save_last_author(author_name)
        else:
            logging.info("No author selected to save.")
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    def on_closing(self):
        """Handle the window close event."""
        # Save the current author if selected
        author_name = self.author_combo.get()
        if author_name:
            self.save_last_author(author_name)
            logging.info(f"Application is closing via window manager. Last author saved: '{author_name}'")
        else:
            logging.info("No author selected upon exit. LastAuthor remains unchanged.")

        # Stop the polling loop and cancel pending callbacks
        self.polling = False
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
            logging.info("Polling loop callback canceled.")

        self.undo_stack.clear()  # Clear undo data

        logging.info("Application is closing.")
        self.destroy()


class QueueHandler(logging.Handler):
    """Custom logging handler that uses a queue."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)