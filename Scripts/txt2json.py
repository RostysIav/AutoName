import json

# Specify the full path to the Char-Refined.txt file
file_path = 'C:/1MYPROG/AutoName/Char-Refined.txt'

# Read the content from the text file with UTF-8 encoding
with open(file_path, 'r', encoding='utf-8') as file:
    characters = file.read().splitlines()

# Create the dictionary with the characters list
data = {
    "characters": characters
}

# Write the dictionary to a JSON file
output_path = 'C:/1MYPROG/AutoName/characters.json'
with open(output_path, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4)

print("JSON file created successfully.")
