import os, json, uuid, argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

CATS = {"billing", "bug", "account", "feature_request", "other"}
PRIOS = {"low", "medium", "high"}
REQ = {"category", "priority", "summary", "tags", "requires_human"}

def call_llm(text, mock=False):
    if mock:
        return '{"category":"billing","priority":"high","summary":"Mock","tags":[],"requires_human":true}'
    
    load_dotenv()
    url = os.getenv("LLM_BASE_URL", "").rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('LLM_API_KEY')}"}
    payload = {"model": os.getenv("LLM_MODEL"), "messages": [
        {"role": "system", "content": 'Верни только JSON: {"category":"...","priority":"..."}'},
        {"role": "user", "content": text}
    ]}
    
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text")
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    text = args.text or input("Текст: ")
    if not text.strip(): return print("Ошибка: пустой ввод")

    try:
        raw = call_llm(text, mock=args.mock)
        data = json.loads(raw)
        
        if REQ - set(data): raise ValueError(f"Нет полей: {REQ - set(data)}")
        if data["category"] not in CATS: raise ValueError("Неверная category")
        if data["priority"] not in PRIOS: raise ValueError("Неверная priority")
        if type(data["requires_human"]) is not bool: raise ValueError("requires_human должен быть bool")

        out = Path("output/result.json")
        out.parent.mkdir(exist_ok=True, parents=True)
        out.write_text(json.dumps({**data, "request_id": str(uuid.uuid4()), "status": "validated"}, ensure_ascii=False, indent=2))
        print("✅ Сохранено в output/result.json")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()