"""
Team Scorpians — Speed Test (10 Questions)
Tests both short and long queries to verify adaptive answer behavior.
"""

import httpx
import time

queries = [
    # Short Queries (1-5 words)
    "What is the capital of Pakistan?",
    "What is 15 + 27?",
    "Who is the founder of Pakistan?",
    "What is the currency of Pakistan?",
    "What is the national language of Pakistan?",
    
    # Medium Queries (6-10 words)
    "Why is Islamabad the capital of Pakistan?",
    "Explain AI in simple terms",
    "What is the boiling point of water?",
    
    # Long Queries (11+ words)
    "Explain the history of Pakistan in detail",
    "Write a short poem about artificial intelligence",
]

print("\n" + "=" * 60)
print("🦂 TEAM SCORPIANS — SPEED TEST (10 Questions)")
print("=" * 60 + "\n")

times = []
results = []

for i, q in enumerate(queries, 1):
    start = time.time()
    try:
        r = httpx.post(
            "http://localhost:8081/chat",  # Port 8081 (agent running here)
            json={"query": q, "api_key": "myHackathonKey2026"},
            timeout=120
        )
        elapsed = time.time() - start
        times.append(elapsed)
        
        if r.status_code == 200:
            data = r.json()
            answer = data.get("answer", "No answer")
            source = data.get("source", "unknown")
            confidence = data.get("confidence", 0)
            latency_ms = data.get("latency_ms", 0)
            
            # Determine answer type
            word_count = len(answer.split())
            if word_count <= 5:
                ans_type = "⚡Short"
            elif word_count <= 20:
                ans_type = "📝Medium"
            else:
                ans_type = "📖Detailed"
            
            results.append({
                "query": q[:40],
                "source": source,
                "confidence": confidence,
                "latency": elapsed,
                "word_count": word_count,
                "type": ans_type
            })
            
            status_emoji = "✅" if source == "local" else "❌" if source == "error" else "⚠️"
            print(f"{status_emoji} Q{i}: {q[:40]}...")
            print(f"   Source: {source} | Type: {ans_type} | Words: {word_count} | Confidence: {confidence:.2f} | Latency: {elapsed:.2f}s\n")
        else:
            print(f"❌ Q{i}: {q[:40]}... Error: {r.status_code}\n")
            
    except Exception as e:
        print(f"❌ Q{i}: {q[:40]}... Error: {str(e)[:50]}\n")

# ============================================================
# SUMMARY
# ============================================================
print("=" * 60)
print("📊 SPEED TEST SUMMARY")
print("=" * 60)

if times:
    print(f"✅ Total Queries: {len(times)}")
    print(f"✅ Average Latency: {sum(times)/len(times):.2f}s")
    print(f"✅ Fastest: {min(times):.2f}s")
    print(f"✅ Slowest: {max(times):.2f}s")
    
    # Source breakdown
    local_count = sum(1 for r in results if r["source"] == "local")
    cache_count = sum(1 for r in results if r["source"] == "cache")
    cloud_count = sum(1 for r in results if r["source"] == "cloud")
    error_count = len(results) - local_count - cache_count - cloud_count
    
    print(f"\n📌 Source Breakdown:")
    print(f"   🏠 Local: {local_count}")
    print(f"   💾 Cache: {cache_count}")
    print(f"   ☁️ Cloud: {cloud_count}")
    print(f"   ❌ Error: {error_count}")
    
    # Answer type breakdown
    short_count = sum(1 for r in results if r["type"] == "⚡Short")
    medium_count = sum(1 for r in results if r["type"] == "📝Medium")
    detailed_count = sum(1 for r in results if r["type"] == "📖Detailed")
    
    print(f"\n📌 Answer Type Breakdown:")
    print(f"   ⚡ Short (<5 words): {short_count}")
    print(f"   📝 Medium (5-20 words): {medium_count}")
    print(f"   📖 Detailed (>20 words): {detailed_count}")

print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)