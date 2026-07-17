import json
with open(r'C:\Users\krazy\.gemini\antigravity-ide\brain\c0b0af9e-8057-4ea8-bed5-a61a089ce89a\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            content = data.get('content', '')
            # I want to find everything the user has ever submitted about mechanics or dice or rolling
            if 'dice' in content.lower() or 'roll' in content.lower() or 'damage' in content.lower() or 'mechanic' in content.lower():
                print(f"--- STEP {data.get('step_index')} ---")
                print(content[:1000] + ("..." if len(content) > 1000 else ""))
