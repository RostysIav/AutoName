import tkinter as tk
from tkinter import filedialog
import re
import os
from datetime import datetime

# Function to process lines
def process_lines(lines):
    processed_lines = []
    seen_lines = set()  # To track duplicates

    for line in lines:
        # Remove leading/trailing whitespaces
        line = line.strip()

        # Check if line contains "The female" (case-insensitive) and skip it
        if re.search(r'\bthe female\b', line, re.IGNORECASE):
            continue

        # Check if the line has a single alphabetical letter, skip if true
        if re.match(r'^[A-Za-z]$', line):
            continue

        # Add line to processed_lines if it's not a duplicate
        if line not in seen_lines:
            processed_lines.append(line)
            seen_lines.add(line)

    return processed_lines

# Main function to read, process, and write the output
def process_file(input_file):
    # Create a meaningful output filename based on input file and current timestamp
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{name}_processed_{timestamp}{ext}"

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
root.title("File Processor with Drag and Drop")

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
