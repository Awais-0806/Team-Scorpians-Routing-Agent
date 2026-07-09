import httpx
import json

url = 'https://api.fireworks.ai/inference/v1/chat/completions'
headers = {
    'Authorization': 'Bearer fw_M8CM2ajLu3hQLSTKZJ21Ti',
    'Content-Type': 'application/json'
}

models_to_test = [
    'accounts/fireworks/models/llama-v3p1-8b-instruct',
    'accounts/fireworks/models/llama-v3p2-1b-instruct',
    'accounts/fireworks/models/phi-3-mini-4k-instruct',
    'accounts/fireworks/models/mixtral-8x7b-instruct',
]

for model in models_to_test:
    print(f"\n Testing model: {model}")
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': 'What is the capital of Pakistan?'}],
        'max_tokens': 50
    }
    try:
        r = httpx.post(url, headers=headers, json=payload, timeout=30)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            answer = data['choices'][0]['message']['content']
            print(f"  Answer: {answer[:100]}")
            print(f"  WORKING! Use this model: {model}")
            break
        else:
            print(f"  Error: {r.text[:100]}")
    except Exception as e:
        print(f"  Exception: {str(e)[:100]}")