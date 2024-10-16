import re
import tkinter as tk
from tkinter import filedialog
import os
from datetime import datetime

# Function to remove square and round brackets with content inside
def remove_brackets(text):
    # Use regular expressions to remove content inside square and round brackets
    text = re.sub(r'\[.*?\]', '', text)  # Remove everything inside square brackets
    text = re.sub(r'\".*?\"', '', text)  # Remove everything inside round brackets
    return text.strip()  # Strip leading/trailing spaces

# Function to process the lines from the file
def process_lines(lines):
    processed_lines = []
    for line in lines:
        processed_line = remove_brackets(line)
        if processed_line:  # If the processed line is not empty
            processed_lines.append(processed_line)
    return processed_lines

# Main function to read, process, and save the output
def process_file(input_file):
    # Create a meaningful output filename based on input file and current timestamp
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{name}_brackets_removed_{timestamp}{ext}"

    # Read and process the file
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        lines = infile.readlines()  # Read all lines

    processed_lines = process_lines(lines)  # Process the lines

    # Write the processed lines to a new file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(processed_lines) + '\n')  # Write processed lines

    print(f"Processing complete. Output saved to {output_file}")
    return output_file

# Function to handle file selection and processing
def select_file():
    input_file = filedialog.askopenfilename(title="Select input file", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if input_file:
        output_file = process_file(input_file)
        result_label.config(text=f"File processed successfully! Output: {output_file}")

# Setting up the GUI window
root = tk.Tk()
root.title("Bracket Remover")

# Window size
root.geometry("400x200")

# Instructions label
label = tk.Label(root, text="Select a file to remove brackets and their content.", pady=20)
label.pack()

# Button to select the file
select_button = tk.Button(root, text="Select File", command=select_file)
select_button.pack()

# Label to display result message
result_label = tk.Label(root, text="", pady=20)
result_label.pack()

# Start the application
root.mainloop()
