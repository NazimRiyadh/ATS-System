import sys
import logging

logging.basicConfig(level=logging.INFO)

print("Attempting to import ats_pipeline...")
try:
    from ats_pipeline import get_pipeline
    print("Import successful.")
    
    print("Attempting to initialize pipeline...")
    pipeline = get_pipeline()
    print("Pipeline initialized successfully.")
    
    print("Attempting to close pipeline...")
    pipeline.close()
    print("Pipeline closed.")
    
except Exception as e:
    print(f"❌ Startup failed: {e}")
    import traceback
    traceback.print_exc()
