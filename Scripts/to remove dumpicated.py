import tkinter as tk
from tkinter import filedialog
import os
from datetime import datetime

# Function to remove duplicate lines
def remove_duplicates(lines):
    seen = set()  # To track unique lines
    unique_lines = []
    
    for line in lines:
        stripped_line = line.strip()  # Strip leading/trailing spaces
        if stripped_line and stripped_line not in seen:  # Check if the line is unique
            unique_lines.append(stripped_line)  # Add unique line to the list
            seen.add(stripped_line)  # Mark line as seen

    return unique_lines

# Main function to read, process, and save the output
def process_file(input_file):
    # Create a meaningful output filename based on input file and current timestamp
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{name}_duplicates_removed_{timestamp}{ext}"

    # Read and process the file
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        lines = infile.readlines()  # Read all lines

    unique_lines = remove_duplicates(lines)  # Remove duplicate lines

    # Write the unique lines to a new file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(unique_lines) + '\n')  # Write unique lines

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
root.title("Duplicate Line Remover")

# Window size
root.geometry("400x200")

# Instructions label
label = tk.Label(root, text="Select a file to remove duplicate lines.", pady=20)
label.pack()

# Button to select the file
select_button = tk.Button(root, text="Select File", command=select_file)
select_button.pack()

# Label to display result message
result_label = tk.Label(root, text="", pady=20)
result_label.pack()

# Start the application
root.mainloop()
