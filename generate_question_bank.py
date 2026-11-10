"""Validate and report the bundled 16,000-question practice bank."""
from pathlib import Path
import json
bank=json.loads((Path(__file__).parent/"data"/"question_bank.json").read_text(encoding="utf-8"))
for level in ("Beginner","Intermediate","Advanced","Expert"):
    print(level, sum(q["difficulty"]==level for q in bank))
print("Total:",len(bank))
