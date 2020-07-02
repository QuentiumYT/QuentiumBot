input()

content_no_comma = []
content_no_backslash = []
content_no_parenthese = []
is_comma = False
is_backslash = False
is_parenthese = False

with open("QuentiumBot.py", "r") as f:
    content_raw = f.readlines()

for x in content_raw:
    if not x == "\n":
        if not is_comma:
            if x[-2] == ",":
                content_no_comma.append(x[:-1] + " ")
                is_comma = True
            else:
                content_no_comma.append(x)
        else:
            if x[-2] == ",":
                x = " ".join(x.split()) + " "
            else:
                is_comma = False
                x = " ".join(x.split()) + "\n"
            content_no_comma[-1] = content_no_comma[-1] + x
    else:
        content_no_comma.append(x)

for x in content_no_comma:
    if not x == "\n":
        if not '\\n" \\' in x:
            if not is_backslash:
                if x[-2] == "\\":
                    content_no_backslash.append(x[:-3] + " ")
                    is_backslash = True
                else:
                    content_no_backslash.append(x)
            else:
                if x[-2] == "\\":
                    x = " ".join(x.split()) + " "
                else:
                    is_backslash = False
                    x = " ".join(x.split()) + "\n"
                content_no_backslash[-1] = content_no_backslash[-1] + x
        else:
            content_no_backslash.append(x)
    else:
        content_no_backslash.append(x)

for x in content_no_backslash:
    if not x == "\n":
        if not is_parenthese:
            if x[-2] == "(":
                content_no_parenthese.append(x[:-1])
                is_parenthese = True
            else:
                content_no_parenthese.append(x)
        else:
            if x[-2] == "(":
                x = " ".join(x.split()) + " "
            else:
                is_parenthese = False
                x = " ".join(x.split()) + "\n"
            content_no_parenthese[-1] = content_no_parenthese[-1] + x
    else:
        content_no_parenthese.append(x)

for x in content_no_parenthese:
    #print(x, end="")
    with open("QuentiumBot2.py", "a") as file:
        file.write(x)
