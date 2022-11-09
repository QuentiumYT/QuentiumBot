import json

# Open the global data file
with open("data.json", "r", encoding="utf-8") as file:
    content = json.load(file)

new_content = content.copy()

# Remove key if commands_server < 10
for srv, data in content.items():
    if data["commands_server"] < 10:
        del new_content[srv]

# Dump the content  to the global data file
with open("data.json", "w", encoding="utf-8") as file:
    json.dump(new_content, file, indent=4)
