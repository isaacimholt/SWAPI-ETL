def is_null(text: str) -> bool:
    return text.lower().strip() in {"none", "n/a", "unknown", "indefinite", ""}
