import re

with open("requirements.txt", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    line = re.sub(r"==.*", "", line)
    new_lines.append(line)

with open("requirements.txt", "w") as f:
    f.writelines(new_lines)
