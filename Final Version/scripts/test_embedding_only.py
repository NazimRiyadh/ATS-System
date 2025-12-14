
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import asyncio
import logging
from src.embedding import get_embedding_model

logging.basicConfig(level=logging.INFO)

def main():
    print("🚀 Testing Embedding Engine...")
    try:
        model = get_embedding_model()
        print("🔧 Model loaded. Encoding text...")
        
        text = "Test sentence."
        embeddings = model.encode(text)
        
        print(f"✅ Success! Embedding shape: {embeddings.shape}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
