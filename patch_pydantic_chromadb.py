import re

config_path = "venv/lib/python3.14/site-packages/chromadb/config.py"
with open(config_path, "r") as f:
    text = f.read()

text = text.replace("Optional[int]", "int")
text = text.replace("Optional[str]", "str")
text = text.replace("Optional[bool]", "bool")
text = text.replace("Optional[float]", "float")
text = text.replace("Optional[Union[bool, str]]", "Union[bool, str]")
text = text.replace("Optional[Dict[str, str]]", "Dict[str, str]")
text = text.replace("Optional[List[str]]", "List[str]")
text = text.replace("Any", "str") 

with open(config_path, "w") as f:
    f.write(text)
