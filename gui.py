# gui.py

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
import configparser
from file_operations import rename_images, rename_images_by_folder_name, rename_images_by_character_name
from data_storage import add_author, load_data, save_data
from logging.handlers import QueueHandler
import queue


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

        # Add DATA_FILE + LOG_FILE as an attribute
        self.DATA_FILE = DATA_FILE
        self.LOG_FILE = LOG_FILE

        # Load data from JSON file
        self.data = load_data(DATA_FILE)
        self.authors = self.data.get('authors', [])
        self.character_names = self.data.get('character_names', [])

        # Create GUI components
        self.create_left_menu()
        self.create_right_menu()
        self.create_main_frame()
        self.create_status_bar()
        self.create_log_window()
        self.setup_logging()

        # Load the last used author
        self.load_last_author()


        # Bind the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_left_menu(self):
        """Create the left menu with Exit and Restart buttons."""
        self.left_frame = tk.Frame(self, width=200, bg='lightgrey')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.exit_button = tk.Button(self.left_frame, text="Exit", command=self.exit_app, width=15)
        self.exit_button.pack(pady=20)

        self.restart_button = tk.Button(self.left_frame, text="Restart", command=self.restart_app, width=15)
        self.restart_button.pack(pady=20)

    def create_right_menu(self):
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
        if author_name:
            success = add_author(author_name, DATA_FILE)
            if success:
                self.authors.append(author_name)
                self.author_combo['values'] = self.authors
                logging.info(f"Added new author: {author_name}")
            else:
                logging.info(f"Author '{author_name}' already exists.")
            self.author_combo.set(author_name)
            self.author_entry.delete(0, tk.END)
            self.save_last_author(author_name)
        else:
            logging.info("No author name entered.")
            
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

    def save_last_author(self, author_name):
        """Save the last used author to the config file."""
        try:
            config['DEFAULT']['LastAuthor'] = author_name
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            logging.info(f"Saved last author to config: {author_name}")
        except Exception as e:
            logging.error(f"Error saving last author to config: {e}")
            
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
        except (PermissionError, FileNotFoundError, OSError) as e:
            # Log the exception
            logging.error(f"Error accessing {abspath}: {e}")

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
            self.prompt_author_name_and_rename(abspath, by_folder_name=True)

    def context_rename_images_by_character_name(self):
        """Context menu action to rename images by character names."""
        item = self.tree.selection()[0]
        abspath = self.tree.set(item, "abspath")
        if os.path.isdir(abspath):
            author_name = self.get_author_name()
            if author_name:
                rename_images_by_character_name(
                    abspath, author_name, self.status_label, self.character_names, self  # Pass 'self' as 'app'
                )


    def prompt_author_name_and_rename(self, folder_path, by_folder_name=False):
        """
        Prompt for the author name and perform the renaming.

        Args:
            folder_path (str): The path of the folder to rename images in.
            by_folder_name (bool): Whether to rename images by folder name.
        """
        author_name = self.get_author_name()
        if author_name:
            if by_folder_name:
                rename_images_by_folder_name(folder_path, author_name, self.status_label)
            else:
                rename_images(folder_path, author_name, self.status_label)

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

        logging.info("Application is closing.")
        self.destroy()

    

class QueueHandler(logging.Handler):
    """Custom logging handler that uses a queue."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)