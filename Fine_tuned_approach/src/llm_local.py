
import os
import aiohttp
import json
import logging
from .config import Config

logger = logging.getLogger("LocalLLM")

async def ollama_model_complete(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    """
    Adapter for LightRAG to use local Ollama model (Flan-T5 or Qwen).
    """
    model_name = kwargs.get("model_name", "qwen2.5:7b") # default
    base_url = "http://localhost:11434/api/chat"

    # --- PROMPT TRACE (PROOF OF CONTEXT) ---
    print("\n" + "="*40 + " PROMPT SENT TO LLM " + "="*40)
    print(f"SYSTEM: {system_prompt[:200]}...")
    print(f"USER PROMPT (Start): {prompt[:500]}")
    if len(prompt) > 500:
        print("... [CONTEXT CONTENT] ...")
        print(f"USER PROMPT (End): {prompt[-300:]}")
    print("="*100 + "\n")
    
    # Save to file for full inspection
    try:
        with open("last_used_prompt.txt", "w", encoding="utf-8") as f:
            f.write(f"=== SYSTEM PROMPT ===\n{system_prompt}\n\n")
            f.write(f"=== USER PROMPT (With Graph Context) ===\n{prompt}")
        print("📝 Full prompt saved to 'last_used_prompt.txt'")
    except Exception as e:
        print(f"⚠️ Failed to save prompt: {e}")
    # ---------------------------------------
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Add history/context
    if history_messages:
        messages.extend(history_messages)
        
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": kwargs.get("temperature", 0.0),
            "num_predict": kwargs.get("max_tokens", 512),
            "num_ctx": 4096, # Optimized for 6GB VRAM (Prevent swapping)
            "num_gpu": 99    # Force GPU layers
        }
    }

    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(base_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama Error {response.status}: {error_text}")
                
                data = await response.json()
                return data["message"]["content"]
                
    except Exception as e:
        logger.error(f"LLM Generation Failed (Ollama): {e}")
        return "" 

