import re

config_path = "venv/lib/python3.14/site-packages/chromadb/config.py"
with open(config_path, "r") as f:
    text = f.read()

text = re.sub(r'Optional\[[^\]]+\]', 'Any', text)

with open(config_path, "w") as f:
    f.write(text)
