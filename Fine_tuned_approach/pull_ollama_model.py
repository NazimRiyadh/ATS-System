
import aiohttp
import asyncio
import json

async def pull_model():
    model_name = "qwen2.5:7b"
    url = "http://localhost:11434/api/pull"
    payload = {"name": model_name}


    
    print(f"Pulling '{model_name}' via API...")
    
    # Increase timeout to 1 hour (3600s) to prevent timeouts on slow connections
    timeout = aiohttp.ClientTimeout(total=3600)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload) as response:
            async for line in response.content:

                if line:
                    try:
                        data = json.loads(line)
                        status = data.get("status")
                        completed = data.get("completed")
                        total = data.get("total")
                        
                        if completed and total:
                            percent = (completed / total) * 100
                            print(f"\rStatus: {status} - {percent:.1f}%", end="")
                        else:
                            print(f"\rStatus: {status}", end="")
                            
                    except:
                        pass
    print("\nModel pulled successfully!")

if __name__ == "__main__":
    asyncio.run(pull_model())
