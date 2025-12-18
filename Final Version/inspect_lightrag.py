
import inspect
from lightrag import LightRAG

print("LightRAG init parameters:")
sig = inspect.signature(LightRAG.__init__)
for name, param in sig.parameters.items():
    print(f"- {name}")
