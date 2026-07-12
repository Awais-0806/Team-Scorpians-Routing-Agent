"""
Hackathon Submission Entrypoint
Reads /input/tasks.json, routes each prompt, writes /output/results.json
"""
import json
import os
import sys
import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv

# ===== LOAD .env FILE =====
load_dotenv()
print("✅ .env loaded!")

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.router import HybridRouter

async def main():
    # 1. Read input
    input_path = Path("/input/tasks.json")
    if not input_path.exists():
        local_input = Path("tasks.json")
        if local_input.exists():
            input_path = local_input
        else:
            print("ERROR: /input/tasks.json not found, and tasks.json not found locally.")
            sys.exit(1)
    
    with open(input_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    
    # 2. Initialize Router
    router = HybridRouter()
    results = []
    
    for task in tasks:
        task_id = task.get("task_id")
        prompt = task.get("prompt")
        
        print(f"Processing {task_id}...")
        start = time.time()
        
        try:
            answer, meta = await router.route(prompt)
            if isinstance(answer, dict):
                answer = json.dumps(answer)
        except Exception as e:
            answer = f"ERROR: {str(e)}"
        
        results.append({
            "task_id": task_id,
            "answer": answer
        })
    
    output_path = Path("/output/results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done. Wrote {len(results)} results to {output_path}")
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())