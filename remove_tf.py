with open("requirements.txt", "r") as f:
    lines = f.readlines()

bad_pkgs = {"tensorflow", "tensorflow-intel", "tensorboard", "tensorboard-data-server", "keras", "optree", "pygame", "pyspark"}
new_lines = []
for line in lines:
    try:
        pkg = line.strip().split(">")[0].split("<")[0].split("=")[0]
        if pkg.lower() not in bad_pkgs and "pygame" not in pkg.lower():
            new_lines.append(line)
    except:
        new_lines.append(line)

with open("requirements.txt", "w") as f:
    f.writelines(new_lines)
