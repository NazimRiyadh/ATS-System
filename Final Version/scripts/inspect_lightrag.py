
import lightrag
import inspect

print("LightRAG dir:", dir(lightrag))
if hasattr(lightrag, "LightRAG"):
    print("LightRAG class dir:", dir(lightrag.LightRAG))

try:
    from lightrag.utils import initialize_pipeline_status
    print("Found initialize_pipeline_status in lightrag.utils")
except ImportError:
    print("Not in lightrag.utils")

try:
    from lightrag.operate import initialize_pipeline_status
    print("Found initialize_pipeline_status in lightrag.operate")
except ImportError:
    print("Not in lightrag.operate")
