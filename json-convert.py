import json

# Step 1: Load your JSON data. If you're reading from a file, use:
with open('excel-to-json.json', 'r') as file:
    original_json = json.load(file)

# Step 2: Create the new structure
desired_structure = {
    "inputs": [],
    "outputs": []
}

# Step 3: Iterate over each category and entry in your original JSON])
for category, entries in original_json.items():
    for entry in entries:
        # Adjusting for the inconsistent key naming for text
        text_key = "Text" if "Text" in entry else "text"
        
        # Handle different variations of the category key
        if "Category" in entry:
            category_key = "Category"
        elif "category" in entry:
            category_key = "category"
        elif "categorization" in entry:
            category_key = "categorization"
        elif "category " in entry:  # Note the space after 'category'
            category_key = "category "
        else:
            # If none of the expected keys are found, print the entry and skip it
            print(f"Missing category key in entry: {entry}")
            continue  # Skip this entry

        # Append the text and category to the new structure
        desired_structure["inputs"].append(entry[text_key])
        desired_structure["outputs"].append(entry[category_key])

# # Step 4: Convert the new structure to JSON format
new_json = json.dumps([desired_structure], indent=2)

# Step 5: Output or save the new JSON
print(new_json)
# To save to a file, use:
# with open('txt_classification_input.json', 'w') as new_file:
#     new_file.write(new_json)
