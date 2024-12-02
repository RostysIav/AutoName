# gui.py
import os
import sys
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import logging
import configparser
from file_operations import rename_images, rename_images_by_folder_name, rename_images_by_character_name, prompt_author_choice
from data_storage import load_data, save_data, add_author, delete_author, add_character_name, delete_character_name
from logging.handlers import QueueHandler
import queue
from PIL import Image, ImageTk, UnidentifiedImageError
import shutil 
import threading


SUPPORTED_IMAGE_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.ico', '.svg', '.heic'
)

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

# Configure the root logger
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Remove any existing handlers
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# FileHandler for writing logs to a file
file_handler = logging.FileHandler(LOG_FILE, mode='a')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

# Now you can log messages
logging.info("Application started. Logging setup complete.")

class App(tk.Tk):
    """Main application class for the Image Renamer."""

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.title("Image Renamer")
        self.geometry("1400x600")

        # Undo operations
        self.undo_stack = []  # Stack to keep track of undo operations

        # Flag to track preview pane visibility
        self.preview_visible = False

        # Load configuration
        self.config = configparser.ConfigParser()
        if not os.path.exists(CONFIG_FILE):
            # Create default config if it doesn't exist
            self.config['DEFAULT'] = {
                'DataFile': DATA_FILE,
                'LogFile': LOG_FILE,
                'LastAuthor': ''
            }
            with open(CONFIG_FILE, 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read(CONFIG_FILE)

        # Load data from JSON file
        self.DATA_FILE = DATA_FILE
        self.LOG_FILE = LOG_FILE
        self.data = load_data(DATA_FILE)
        self.authors = self.data.get('authors', [])
        self.character_names = self.data.get('character_names', [])

        # **Load icons BEFORE creating the main frame**
        self.load_icons()

        # Create GUI components
        self.create_left_menu()
        self.create_right_menu()
        self.load_icons()
        self.create_main_frame()
        self.create_status_bar()
        self.create_log_window()
        self.create_preview_pane()  # Ensure this is called after create_main_frame
        self.create_undo_button()
        self.setup_logging()
        self.create_toggle_preview_button()

        # Initialize a queue for progress updates
        self.progress_queue = queue.Queue()
        self.after(100, self.process_progress_queue)

        # Confirm image_label existence
        if hasattr(self, 'image_label'):
            logging.info("image_label has been successfully created.")
        else:
            logging.error("Failed to create image_label.")

        # Load the last used author
        self.load_last_author()

        # Bind the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.operation_mode = tk.StringVar(value="Rename")  # Default operation mode
        self.create_operation_mode_selector()

    def load_icons(self):
        """Load folder and file icons for the tree view."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, "assets")
        folder_icon_path = os.path.join(assets_dir, "folder_icon.png")
        file_icon_path = os.path.join(assets_dir, "file_icon.png")
        
        try:
            folder_img = Image.open(folder_icon_path).resize((16, 16), Image.ANTIALIAS)
            self.folder_icon = ImageTk.PhotoImage(folder_img)
            logging.info(f"Loaded folder icon from '{folder_icon_path}'")
        except Exception as e:
            logging.error(f"Failed to load folder icon from '{folder_icon_path}': {e}")
            self.folder_icon = None  # Fallback to default icon or no icon

        try:
            file_img = Image.open(file_icon_path).resize((16, 16), Image.ANTIALIAS)
            self.file_icon = ImageTk.PhotoImage(file_img)
            logging.info(f"Loaded file icon from '{file_icon_path}'")
        except Exception as e:
            logging.error(f"Failed to load file icon from '{file_icon_path}': {e}")
            self.file_icon = None  # Fallback to default icon or no icon

    def create_left_menu(self):
        """Create the left menu with Exit and Restart buttons."""
        self.left_frame = tk.Frame(self, width=200, bg='lightgrey')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.exit_button = tk.Button(self.left_frame, text="Exit", command=self.exit_app, width=15)
        self.exit_button.pack(pady=20)

        self.restart_button = tk.Button(self.left_frame, text="Restart", command=self.restart_app, width=15)
        self.restart_button.pack(pady=20)

    def create_right_menu(self):
        """Create the right menu for author and character name management."""
        self.right_frame = tk.Frame(self, width=200, bg='lightgrey')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Author section
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

        # Undo Delete Button for Authors
        self.undo_delete_author_button = tk.Button(
            self.right_frame, text="Undo Delete Author", command=self.undo_last_deletion
        )
        self.undo_delete_author_button.pack(pady=5)

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

        # Undo Delete Button for Characters
        self.undo_delete_character_button = tk.Button(
            self.right_frame, text="Undo Delete Character", command=self.undo_last_deletion
        )
        self.undo_delete_character_button.pack(pady=5)

    def create_main_frame(self):
        """Create the main frame containing the directory entry, search bar, and tree view."""
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Entry and Go button frame
        self.entry_frame = tk.Frame(self.main_frame)
        self.entry_frame.pack(fill=tk.X, pady=5)

        self.path_entry = tk.Entry(self.entry_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.go_button = tk.Button(self.entry_frame, text="Go", command=self.load_path)
        self.go_button.pack(side=tk.LEFT, padx=5)

        # Search frame
        self.search_frame = tk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, pady=5)

        self.search_label = tk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = tk.Button(self.search_frame, text="Go", command=self.search_tree)
        self.search_button.pack(side=tk.LEFT, padx=5)

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

        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Rename Images", command=self.context_rename_images)
        self.context_menu.add_command(label="Rename Images by Folder Name", command=self.context_rename_images_by_folder_name)
        self.context_menu.add_command(label="Rename Images by Character Name", command=self.context_rename_images_by_character_name)

    def create_status_bar(self):
        """Create the status bar at the bottom of the application."""
        self.status_frame = tk.Frame(self, bg='lightgrey')
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(self.status_frame, text="Status: Ready", anchor='w', bg='lightgrey')
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(self.status_frame, orient='horizontal', length=200, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=5)

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
        logging.info("Creating preview pane.")
        self.preview_frame = tk.Frame(self.main_frame, width=200, bg='white')
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.preview_label = tk.Label(self.preview_frame, text="Preview")
        self.preview_label.pack()

        self.image_label = tk.Label(self.preview_frame, text="No file selected.")
        self.image_label.pack(pady=10)
        
        # Confirm initialization
        if hasattr(self, 'image_label'):
            logging.info("image_label has been successfully created.")
        else:
            logging.error("Failed to create image_label.")

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
        """Create the Undo button and place it in the status bar."""
        self.undo_button = tk.Button(self.status_frame, text="Undo", command=self.undo_last_action)
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
                save_data(self.DATA_FILE, self.data)
                logging.info(f"Restored author: {name}")
                messagebox.showinfo("Undo Successful", f"Author '{name}' has been restored.")
            elif action_type == 'character':
                self.character_names.append(name)
                self.character_names = sorted(self.character_names)
                self.character_name_combo['values'] = self.character_names
                self.data['character_names'] = self.character_names
                save_data(self.DATA_FILE, self.data)
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
                        if original_file and os.path.exists(new_file):
                            os.rename(new_file, original_file)
                            logging.info(f"Reverted '{new_file}' to '{original_file}'")
                    elif operation_mode == "Copy":
                        if os.path.exists(new_file):
                            os.remove(new_file)
                            logging.info(f"Removed copied file '{new_file}'")
                    elif operation_mode == "Move":
                        if original_file and os.path.exists(new_file):
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
        try:
            selected_item = self.tree.selection()[0]
            abspath = self.tree.set(selected_item, "abspath")
            if os.path.isfile(abspath):
                self.show_image_preview(abspath)
            else:
                # Clear the preview if a directory is selected
                self.image_label.config(image='', text="No file selected.")
                self.image_label.image = None
        except IndexError:
            # No item selected
            self.image_label.config(image='', text="No file selected.")
            self.image_label.image = None

    def show_image_preview(self, image_path):
        """Display a thumbnail of the selected image or indicate non-image files."""
        if not image_path.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS):
            # Clear any existing image and show a message
            self.image_label.config(image='', text="No preview available for this file.")
            self.image_label.image = None
            return

        try:
            img = Image.open(image_path)
            img.thumbnail((200, 200))  # Adjust the size as needed
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference to prevent garbage collection
        except UnidentifiedImageError:
            logging.warning(f"Unsupported image format: {image_path}")
            self.image_label.config(image='', text="Cannot preview this image format.")
            self.image_label.image = None
        except Exception as e:
            logging.error(f"Error loading image '{image_path}': {e}")
            self.image_label.config(image='', text="Error loading image.")
            self.image_label.image = None

    #Preview image toggle 
    def create_toggle_preview_button(self):
        """Create a button to toggle the preview pane."""
        self.toggle_preview_button = tk.Button(self.main_frame, text="Toggle Preview", command=self.toggle_preview)
        self.toggle_preview_button.pack(side=tk.TOP, fill=tk.X, pady=5)

    def create_preview_pane(self):
        """Create a pane to display image thumbnails."""
        self.preview_frame = tk.Frame(self.main_frame, width=200, bg='white')
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.preview_label = tk.Label(self.preview_frame, text="Preview")
        self.preview_label.pack()

        self.image_label = tk.Label(self.preview_frame, text="No file selected.")
        self.image_label.pack(pady=10)

        # Confirm initialization
        if hasattr(self, 'image_label'):
            logging.info("image_label has been successfully created.")
        else:
            logging.error("Failed to create image_label.")

    def toggle_preview(self):
        """Show or hide the preview pane."""
        if self.preview_visible:
            self.preview_frame.pack_forget()
            self.preview_visible = False
            logging.info("Preview pane hidden.")
        else:
            self.preview_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
            self.preview_visible = True
            logging.info("Preview pane displayed.")

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
            
    def preview_selected_image(self):
        """Preview the selected image in the preview pane."""
        try:
            # Assuming the treeview is named 'file_list'
            selected_item = self.file_list.selection()

            # Check if an item is selected
            if not selected_item:
                self.image_label.config(text="No file selected.")
                logging.warning("No file selected for preview.")
                return

            # Get the file path of the selected item
            selected_file_path = self.file_list.item(selected_item, 'values')[0]

            # Verify if the path points to a file
            if not os.path.isfile(selected_file_path):
                self.image_label.config(text="File not found.")
                logging.warning(f"File not found for preview: {selected_file_path}")
                return

            # Load the image
            img = Image.open(selected_file_path)
            img.thumbnail((200, 200), Image.ANTIALIAS)  # Resize the image to fit the preview pane

            # Update the preview pane
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference to avoid garbage collection
            logging.info(f"Previewed image: {selected_file_path}")

        except Exception as e:
            # Log the error and update the preview label with an error message
            logging.error(f"Failed to preview image: {e}")
            self.image_label.config(text="Failed to load image.")

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
            success = add_author(author_name, self.DATA_FILE)
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
            success = add_character_name(character_name, self.DATA_FILE)
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
            success = delete_author(author_name, self.DATA_FILE)
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
            success = delete_character_name(character_name, self.DATA_FILE)
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
                    save_data(self.DATA_FILE, self.data)
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
            self.config['DEFAULT']['LastAuthor'] = author_name
            with open(CONFIG_FILE, 'w') as configfile:
                self.config.write(configfile)
            logging.info(f"Saved last author to config: {author_name}")
        except Exception as e:
            logging.error(f"Error saving last author to config: {e}")    
  
    def load_last_author(self):
        """Load the last used author from the config file."""
        try:
            author_name = self.config['DEFAULT'].get('LastAuthor', '').strip()
            if author_name:
                if author_name not in self.authors:
                    self.authors.append(author_name)
                    self.author_combo['values'] = self.authors
                    self.data['authors'] = self.authors
                    save_data(self.DATA_FILE, self.data)
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
        """Insert a node into the tree view with appropriate icon."""
        if os.path.isdir(abspath):
            icon = self.folder_icon if self.folder_icon else ""
            node = self.tree.insert(parent, 'end', text=text, open=False, image=icon)
            self.tree.set(node, "abspath", abspath)
            self.tree.insert(node, 'end')  # Insert dummy child
        else:
            icon = self.file_icon if self.file_icon else ""
            node = self.tree.insert(parent, 'end', text=text, open=False, image=icon)
            self.tree.set(node, "abspath", abspath)

    def on_open_node(self, event):
        """Handle the event when a node is opened."""
        node = self.tree.focus()
        abspath = self.tree.set(node, "abspath")

        # Check if the node has a dummy child
        children = self.tree.get_children(node)
        if len(children) == 1:
            child_abspath = self.tree.set(children[0], "abspath")
            if not child_abspath:  # Dummy child has empty abspath
                # Remove dummy child
                self.tree.delete(children[0])

                # Populate with actual children
                try:
                    for p in sorted(os.listdir(abspath)):
                        child_path = os.path.join(abspath, p)
                        if os.path.isdir(child_path) or os.path.isfile(child_path):
                            self.insert_node(node, p, child_path)
                except (PermissionError, FileNotFoundError, OSError) as e:
                    logging.error(f"Error accessing {abspath}: {e}")

    def prompt_author_name_and_rename(self, folder_path, by_folder_name=False):
        """
        Prompt for author name and perform renaming or copying/moving.
        """
        folder_name = os.path.basename(folder_path)
        preselected_author = self.get_author_name()

        # Ask user to choose how to set the author
        chosen_author = prompt_author_choice(folder_name, preselected_author)
        if not chosen_author:
            return  # User canceled the operation

        operation_mode = self.operation_mode.get()
        destination_folder = None

        if operation_mode in ["Copy", "Move"]:
            destination_folder = filedialog.askdirectory(title="Select Destination Folder", parent=self)
            if not destination_folder:
                messagebox.showwarning("No Destination", "Operation canceled. No destination folder selected.", parent=self)
                return

        # Start the file renaming process in a separate thread
        thread = threading.Thread(
            target=self.run_rename_images_by_folder_name if by_folder_name else self.run_rename_images,
            args=(folder_path, chosen_author, operation_mode, destination_folder)
        )
        thread.start()


    def run_rename_images(self, folder_path, author_name, operation_mode, destination_folder):
        """Run the rename_images operation in a separate thread."""
        rename_images(
            folder_path,
            author_name,
            self.status_label,
            self,
            operation_mode,
            destination_folder,
            progress_callback=self.update_progress
        )

    def run_rename_images_by_folder_name(self, folder_path, author_name, operation_mode, destination_folder):
        """Run the rename_images_by_folder_name operation in a separate thread."""
        rename_images_by_folder_name(
            folder_path,
            author_name,
            self.status_label,
            self,
            operation_mode,
            destination_folder,
            progress_callback=self.update_progress
        )

    def run_rename_images_by_character_name(self, folder_path, author_name, operation_mode, destination_folder):
        """Run the rename_images_by_character_name operation in a separate thread."""
        rename_images_by_character_name(
            folder_path,
            author_name,
            self.status_label,
            self.character_names,
            self,
            operation_mode,
            destination_folder,
            progress_callback=self.update_progress
        )

    def update_progress(self, status, data=None):
        """Callback function to update progress."""
        if status == "start":
            total = data
            self.progress_queue.put(("start", total))
        elif status == "update":
            increment = data
            self.progress_queue.put(("update", increment))
        elif status == "skipped":
            skipped_message = data
            self.progress_queue.put(("skipped", skipped_message))
        elif status == "done":
            self.progress_queue.put(("done",))
        elif status == "error":
            error_message = data
            self.progress_queue.put(("error", error_message))

    def show_context_menu(self, event):
        """Show the context menu on right-click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def context_rename_images(self):
        """Context menu action to rename images."""
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a directory to rename images.")
            logging.warning("Rename Images action invoked without any selection.")
            return
        
        item = selected_items[0]
        abspath = self.tree.set(item, "abspath")
        
        if os.path.isdir(abspath):
            logging.info(f"Initiating rename operation on directory: {abspath}")
            self.prompt_author_name_and_rename(abspath)
        else:
            messagebox.showwarning("Invalid Selection", "Selected item is not a directory.")
            logging.warning(f"Rename Images action invoked on a non-directory item: {abspath}")

    def context_rename_images_by_folder_name(self):
        """Context menu action to rename images by folder name."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a directory to rename images by folder name.")
            logging.warning("Rename Images by Folder Name action invoked without any selection.")
            return

    def context_rename_images_by_character_name(self):
        """Context menu action to rename images by character names."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a directory to rename images by character names.")
            logging.warning("Rename Images by Character Name action invoked without any selection.")
            return

        item = selected_items[0]
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

                # Start file operation in a new thread
                thread = threading.Thread(target=self.run_rename_images_by_character_name, args=(abspath, author_name, operation_mode, destination_folder))
                thread.start()
        else:
            messagebox.showwarning("Invalid Selection", "Selected item is not a directory.")
            logging.warning(f"Rename Images by Character Name action invoked on a non-directory item: {abspath}")

    def load_path(self):
        """Load the path entered in the path entry."""
        path = self.path_entry.get()
        if os.path.isdir(path):
            self.tree.delete(*self.tree.get_children())
            base_name = os.path.basename(path.rstrip(os.sep))
            if not base_name:
                # For root directories like 'C:/', os.path.basename may return empty
                base_name = path
            self.insert_node('', base_name, path)
            self.populate_tree('', path)
            self.status_label.config(text=f"Loaded path: {path}")
            logging.info(f"Loaded path: {path}")
        else:
            messagebox.showerror("Error", "Invalid directory path")
            self.status_label.config(text="Invalid directory path")
            logging.error(f"Invalid directory path entered: {path}")

    def populate_tree(self, parent, path):
        """Populate the tree view with directories and all files."""
        try:
            for p in sorted(os.listdir(path)):
                abspath = os.path.join(path, p)
                if os.path.isdir(abspath):
                    self.insert_node(parent, p, abspath)
                else:
                    self.insert_node(parent, p, abspath)
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

    def search_tree(self):
        """Search for a file or directory in the tree view."""
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search query.")
            return

        # Collapse all nodes first
        for node in self.tree.get_children():
            self.tree.item(node, open=False)
            self.collapse_all_children(node)

        # Search and highlight matching nodes
        matching_nodes = self.find_matching_nodes('', query)
        if matching_nodes:
            for node in matching_nodes:
                # Open parent nodes
                self.open_parent_nodes(node)
                # Select and focus the node
                self.tree.selection_set(node)
                self.tree.focus(node)
                self.tree.see(node)
        else:
            messagebox.showinfo("No Results", f"No files or directories match '{query}'.")

    def find_matching_nodes(self, parent, query):
        """Recursively find all nodes that match the query."""
        matches = []
        for child in self.tree.get_children(parent):
            node_text = self.tree.item(child, 'text').lower()
            if query in node_text:
                matches.append(child)
            # Recursively search in children
            matches.extend(self.find_matching_nodes(child, query))
        return matches

    def open_parent_nodes(self, node):
        """Open all parent nodes of a given node."""
        parent = self.tree.parent(node)
        if parent:
            self.tree.item(parent, open=True)
            self.open_parent_nodes(parent)

    def process_progress_queue(self):
        """Process progress updates from the queue."""
        try:
            while True:
                message = self.progress_queue.get_nowait()
                if message[0] == "start":
                    total = message[1]
                    self.progress['maximum'] = total
                    self.progress['value'] = 0
                    self.progress.start(10)  # Start indeterminate progress
                    self.status_label.config(text="Operation started...")
                elif message[0] == "update":
                    increment = message[1]
                    self.progress['value'] += increment
                    self.status_label.config(text=f"Processing... ({self.progress['value']}/{self.progress['maximum']})")
                elif message[0] == "skipped":
                    skipped_message = message[1]
                    messagebox.showinfo("Skipped Files", skipped_message)
                    logging.info(skipped_message)
                elif message[0] == "done":
                    self.progress.stop()
                    self.progress['value'] = 0
                    self.status_label.config(text="Operation completed.")
                    messagebox.showinfo("Success", "Operation completed successfully.")
                elif message[0] == "error":
                    error_message = message[1]
                    self.progress.stop()
                    self.progress['value'] = 0
                    self.status_label.config(text="Operation encountered errors.")
                    messagebox.showerror("Error", error_message)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_progress_queue)

    def collapse_all_children(self, node):
        """Recursively collapse all children of a node."""
        for child in self.tree.get_children(node):
            self.tree.item(child, open=False)
            self.collapse_all_children(child)

class QueueHandler(logging.Handler):
    """Custom logging handler that uses a queue."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

if __name__ == "__main__":
    app = App()
    app.mainloop()