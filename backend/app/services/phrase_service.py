def process_phrase_submission(japanese: str, english: str) -> dict[str, int | str]:
    normalized_japanese = japanese.strip()
    normalized_english = english.strip()

    if not normalized_japanese or not normalized_english:
        raise ValueError("Both Japanese and English are required.")

    return {
        "status": "received",
        "japanese_length": len(normalized_japanese),
        "english_length": len(normalized_english),
    }
