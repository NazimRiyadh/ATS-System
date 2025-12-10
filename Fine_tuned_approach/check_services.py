
from lightrag import LightRAG
import inspect

try:
    print("ainsert Signature:")
    print(inspect.signature(LightRAG.ainsert))
except Exception as e:
    print(f"Error: {e}")
