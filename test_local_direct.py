import asyncio
import sys
sys.path.insert(0, r"D:\AMD Hackathone project\files")

from app.clients import LocalLLMClient

async def main():
    print("=" * 60)
    print("🦂 TESTING LOCALLLMCLIENT DIRECTLY")
    print("=" * 60)
    
    client = LocalLLMClient()
    print(f"🔗 URL: {client.base_url}")
    print(f"📦 Model: {client.model_name}")
    print("\n📤 Sending query: 'What is 2+2?'")
    
    try:
        answer = await client.generate("What is 2+2?", max_tokens=128)
        print("\n✅ SUCCESS!")
        print(f"📥 Answer: {answer}")
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}")
        print(f"📝 Error: {str(e)}")

asyncio.run(main())