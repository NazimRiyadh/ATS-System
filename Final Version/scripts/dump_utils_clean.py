
import inspect
import lightrag.utils

if hasattr(lightrag.utils, "split_string_by_multi_markers"):
    print(inspect.getsource(lightrag.utils.split_string_by_multi_markers))
