# Flan-T5 Experiment Guide 🧪

This guide explains how to set up a **completely separate environment** to test Google's Flan-T5 model without breaking your main ATS.

## 1. Create a New Folder

Do this **outside** your current `Fine_tuned_approach` folder.

```bash
cd ..
mkdir flan_t5_lab
cd flan_t5_lab
```

## 2. Create a Virtual Environment (Crucial)

You need a fresh python environment because we will install PyTorch (2GB+).

```bash
python -m venv venv
# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate
```

## 3. Install Dependencies

Create a `requirements.txt` file in the new folder:

```text
torch --index-url https://download.pytorch.org/whl/cu118  # If you have NVIDIA GPU
transformers
accelerate
sentencepiece
```

Run: `pip install -r requirements.txt`

## 4. The Inference Script (`run_flan.py`)

Create this python file to test the model:

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Model Choice: "google/flan-t5-small", "base", "large", "xl", "xxl"
MODEL_NAME = "google/flan-t5-large"

print(f"Loading {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, device_map="auto")

def ask_flan(prompt):
    input_text = prompt
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda" if torch.cuda.is_available() else "cpu")

    outputs = model.generate(input_ids, max_length=512)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    prompt = "Review this candidate: 'John is a Python dev with 5 years exp.' Is he senior?"
    print("\nPrompt:", prompt)
    print("Answer:", ask_flan(prompt))
```

## 5. Why Separate?

- **Size**: This setup pulls gigabytes of model weights immediately.
- **Conflicts**: `torch` versions often conflict with other libraries.
- **Safety**: If this crashes, your main ATS (`uvicorn`) keeps running perfectly.
