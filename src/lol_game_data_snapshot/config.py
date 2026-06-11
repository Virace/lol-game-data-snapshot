from __future__ import annotations


def parse_languages(value: str) -> list[str]:
    languages = [item.strip() for item in value.split(",") if item.strip()]
    if "default" not in languages:
        languages.insert(0, "default")
    return languages

