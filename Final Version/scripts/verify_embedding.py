
import sys
import os
import asyncio
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.embedding import get_embedding_model

async def main():
    print("Testing Local (Hugging Face) Embedding Model...")
    
    try:
        model = get_embedding_model()
        print(f"Model initialized. Device: {model.device}")
        
        text = "This is a test sentence for embedding generation."
        print(f"Generating embedding for: '{text}'")
        
        # Test sync encode
        embedding = model.encode(text)
        print(f"Success! Embedding shape: {embedding.shape}")
        
        if embedding.shape[1] == 1024:
             print("✅ Dimension check passed (1024)")
        else:
             print(f"❌ Dimension mismatch. Expected 1024, got {embedding.shape[1]}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
