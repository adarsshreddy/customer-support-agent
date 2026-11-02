import json
import re
from pathlib import Path


FAQ_PATH = Path(__file__).with_name("faqs.json")

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "can",
    "do",
    "does",
    "for",
    "how",
    "i",
    "is",
    "me",
    "my",
    "of",
    "the",
    "to",
    "what",
    "when",
    "where",
    "your",
}


def load_faqs() -> list[dict[str, str]]:
    """Load and validate the FAQ file next to this module."""
    with FAQ_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"{FAQ_PATH.name} must contain a JSON list.")

    faqs: list[dict[str, str]] = []
    for index, item in enumerate(data, start=1):
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("question"), str)
            or not isinstance(item.get("answer"), str)
        ):
            raise ValueError(
                f"FAQ entry {index} must have string question and answer fields."
            )
        faqs.append({"question": item["question"], "answer": item["answer"]})

    return faqs


def _tokens(text: str) -> set[str]:
    words = set(re.findall(r"[a-z0-9]+", text.casefold()))
    return words - _STOP_WORDS


def find_best_faq(
    query: str, faqs: list[dict[str, str]], threshold: float = 0.6
) -> dict[str, str] | None:
    """Return a sufficiently relevant FAQ, or None when no safe match exists."""
    query_words = _tokens(query)
    if len(query_words) < 2:
        return None

    best_faq: dict[str, str] | None = None
    best_score = 0.0
    for faq in faqs:
        faq_words = _tokens(faq["question"])
        score = len(query_words & faq_words) / len(query_words)
        if score > best_score:
            best_score = score
            best_faq = faq

    return best_faq if best_score >= threshold else None
