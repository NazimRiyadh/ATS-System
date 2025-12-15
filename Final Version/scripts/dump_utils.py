
import inspect
import lightrag.utils
try:
    # Try to find the function that splits strings
    # Based on error "found 2/4 feilds"
    # It might be named verify or split
    # Let's list members
    print("Members of lightrag.utils:")
    for name, obj in inspect.getmembers(lightrag.utils):
        if inspect.isfunction(obj):
            print(f"- {name}")
            
    # If I find split_string_by_multi_markers, dump it
    if hasattr(lightrag.utils, "split_string_by_multi_markers"):
        source = inspect.getsource(lightrag.utils.split_string_by_multi_markers)
        print("\nSource of split_string_by_multi_markers:")
        print(source)
except Exception as e:
    print(f"Error: {e}")
