
import torch
import sys

def check_gpu():
    print(f"Python: {sys.version}")
    print(f"Torch: {torch.__version__}")
    
    if torch.cuda.is_available():
        print("✅ CUDA is available!")
        print(f"   Device: {torch.cuda.get_device_name(0)}")
        print(f"   Count: {torch.cuda.device_count()}")
    else:
        print("❌ CUDA is NOT available.")
        
check_gpu()
