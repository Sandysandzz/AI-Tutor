import re

file_paths = [
    "venv/lib/python3.14/site-packages/chromadb/config.py",
    # We might need to patch more files in chromadb if there are more errors.
]

for path in file_paths:
    try:
        with open(path, "r") as f:
            text = f.read()

        # Replace `Optional[TYPE]` with `TYPE | None`
        # Because non-greedy matching might break on nested brackets like `Optional[Dict[str, str]]`, 
        # let's just use exact string replacements for known types in config.py
        text = text.replace("Optional[int]", "int | None")
        text = text.replace("Optional[str]", "str | None")
        text = text.replace("Optional[bool]", "bool | None")
        text = text.replace("Optional[float]", "float | None")
        text = text.replace("Optional[Union[bool, str]]", "Union[bool, str] | None")
        text = text.replace("Optional[Dict[str, str]]", "Dict[str, str] | None")
        text = text.replace("Optional[List[str]]", "List[str] | None")
        
        # Also fix the import if Any was replaced by str
        # Not needed since we will force reinstall chromadb first!

        with open(path, "w") as f:
            f.write(text)
    except FileNotFoundError:
        pass
