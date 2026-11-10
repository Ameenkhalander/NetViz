import json
from pathlib import Path

def test_bank_has_4000_questions_per_level():
    bank=json.loads((Path(__file__).parents[1]/"data/question_bank.json").read_text(encoding="utf-8"))
    assert len(bank)==16000
    for level in ("Beginner","Intermediate","Advanced","Expert"):
        assert sum(q["difficulty"]==level for q in bank)==4000

def test_questions_have_valid_answers_and_references():
    bank=json.loads((Path(__file__).parents[1]/"data/question_bank.json").read_text(encoding="utf-8"))
    assert len({q["id"] for q in bank})==16000
    assert len({q["question"] for q in bank})==16000
    for q in bank:
        assert q["question"] and len(q["options"])==4
        assert 0 <= q["correct_index"] < 4
        assert q["explanation"] and q["source_url"]
