import json

new_lang = input("New lang letters (ex. nl): ")

# Open the tranlations file
with open("../data/translations.json", "r", encoding="utf-8") as file:
    content = json.load(file)

# Convert loop all main keys
for command in content.keys():
    # Skip TYPE keys (for anchors)
    if not "TYPE" in command:
        content[command][new_lang] = content[command]["en"] # Create a copy of english

# Dump the content to on other translations file
with open("../data/translations2.json", "w", encoding="utf-8") as file:
    json.dump(content, file, indent=4, ensure_ascii=False) # Do not ensure ASCII to keep accents
