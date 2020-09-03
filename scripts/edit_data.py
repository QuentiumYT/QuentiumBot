import json

# Open the global data file
with open("data.json", "r", encoding="utf-8") as file:
    content = json.load(file)

# Convert autorole_server data to int
for srv in content.keys():
    autorole = content[srv]["autorole_server"]
    if autorole:
        content[srv]["autorole_server"] = int(autorole)

# Dump the content  to the global data file
with open("data.json", "w", encoding="utf-8") as file:
    json.dump(content, file, indent=4)
