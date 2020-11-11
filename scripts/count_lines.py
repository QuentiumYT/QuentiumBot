import glob

names = {}
for fn in glob.iglob("../**/*.py", recursive=True):
    with open(fn, encoding="utf-8") as f:
        names[fn] = sum(1 for line in f if line)

print(sum(names.values()))
