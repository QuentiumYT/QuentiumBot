import json

lang_reset = input("Lang to reset (ex. nl): ")

# Open the tranlations file
with open("../data/translations.json", "r", encoding="utf-8") as file:
    content = json.load(file)

# Convert loop all main keys
for command in content.keys():
    # Skip TYPE keys (for anchors)
    if not "TYPE" in command:
        msg_keys = content[command][lang_reset]
        for subkey, subvalue in msg_keys.items():
            # Keys that are translation messages
            if "msg_" in subkey:
                # If it's only a string, reset it
                if type(subvalue) == str:
                    content[command][lang_reset][subkey] = ""

# Dump the content to on other translations file
with open("../data/translations2.json", "w", encoding="utf-8") as file:
    json.dump(content, file, indent=4, ensure_ascii=False) # Do not ensure ASCII to keep accents
