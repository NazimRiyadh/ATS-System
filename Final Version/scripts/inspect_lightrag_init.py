
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lightrag import LightRAG
import inspect

print("LightRAG.__init__ signature:")
print(inspect.signature(LightRAG.__init__))
