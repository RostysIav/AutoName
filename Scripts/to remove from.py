import tkinter as tk
from tkinter import filedialog
import os

# Function to process each line and keep everything before "from"
def process_line(line):
    # Find the word "from" (case-insensitive) and split before it
    split_index = line.lower().find("from")
    if split_index != -1:
        return line[:split_index].strip()  # Keep everything before "from"
    return line.strip()  # If "from" is not found, keep the whole line

# Main function to process the file
def keep_until_from(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Process each line and write to the output file
            processed_line = process_line(line)
            if processed_line:  # Only write non-empty lines
                outfile.write(processed_line + '\n')
    print(f"Processing complete. Output saved to {output_file}")
    
# Function to handle file selection and processing
def select_file():
    input_file = filedialog.askopenfilename(title="Select input file", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if input_file:
        # Output file will be created in the same directory as input file
        output_file = os.path.join(os.path.dirname(input_file), 'output.txt')
        keep_until_from(input_file, output_file)
        result_label.config(text=f"File processed successfully! Output: {output_file}")

# Setting up the GUI window
root = tk.Tk()
root.title("Drag and Drop File Processor")

# Window size
root.geometry("400x200")

# Instructions label
label = tk.Label(root, text="Drag and drop a file or click below to select a file.", pady=20)
label.pack()

# Button to select the file
select_button = tk.Button(root, text="Select File", command=select_file)
select_button.pack()

# Label to display result message
result_label = tk.Label(root, text="", pady=20)
result_label.pack()

# Start the application
root.mainloop()
