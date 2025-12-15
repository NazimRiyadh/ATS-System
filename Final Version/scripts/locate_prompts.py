
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from lightrag.utils import PROMPTS
    print("Found PROMPTS in lightrag.utils")
    print(f"Keys: {list(PROMPTS.keys())}")
except ImportError:
    print("PROMPTS not in lightrag.utils")

try:
    from lightrag.prompt import PROMPTS
    print("Found PROMPTS in lightrag.prompt")
except ImportError:
    print("PROMPTS not in lightrag.prompt")
