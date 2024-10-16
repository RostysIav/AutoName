import tkinter as tk
from tkinter import filedialog
import os
from datetime import datetime

# Function to break lines at each comma and remove the comma
def break_lines_at_comma(lines):
    processed_lines = []
    for line in lines:
        # Split the line by commas and store each part in a new line
        parts = line.split(',')
        for part in parts:
            processed_lines.append(part.strip())  # Add each part as a separate line and strip leading/trailing spaces
    return processed_lines

# Main function to read, process, and save the output
def process_file(input_file):
    # Create a meaningful output filename based on input file and current timestamp
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{name}_comma_removed_{timestamp}{ext}"

    # Read and process the file
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
        lines = infile.readlines()  # Read all lines

    processed_lines = break_lines_at_comma(lines)  # Process the lines

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
root.title("Comma Line Breaker and Remover")

# Window size
root.geometry("400x200")

# Instructions label
label = tk.Label(root, text="Select a file to break lines at commas and remove commas.", pady=20)
label.pack()

# Button to select the file
select_button = tk.Button(root, text="Select File", command=select_file)
select_button.pack()

# Label to display result message
result_label = tk.Label(root, text="", pady=20)
result_label.pack()

# Start the application
root.mainloop()
