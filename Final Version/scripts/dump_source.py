
import inspect
from lightrag.operate import extract_entities
import sys

try:
    source = inspect.getsource(extract_entities)
    with open("temp_extract_entities_source.py", "w", encoding="utf-8") as f:
        f.write(source)
    print("Source code saved to temp_extract_entities_source.py")
except Exception as e:
    print(f"Error: {e}")
