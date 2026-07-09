import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.3

@app.post("/generate")
async def generate(req: GenerateRequest):
    query = req.prompt.replace("<start_of_turn>user\n", "").replace("<end_of_turn>\n<start_of_turn>model\n", "").strip()
    # Fun mock answers
    if "2+2" in query or "2 + 2" in query:
        answer = "4"
    elif "capital of France" in query.lower():
        answer = "Paris"
    elif "hi" in query.lower() or "hello" in query.lower():
        answer = "Hello! I am your local AI assistant running on AMD GPU."
    else:
        answer = f"Local model says: '{query[:40]}...' is an interesting question."
    return {"text": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)