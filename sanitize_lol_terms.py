import argparse
import json
import re
from pathlib import Path


REPLACEMENTS = [
    (re.compile(r"guardian angel", re.IGNORECASE), "rewind"),
    (re.compile(r"godlike", re.IGNORECASE), "unstoppable"),
    (re.compile(r"goddess", re.IGNORECASE), ""),
    (re.compile(r"\bgods\b", re.IGNORECASE), ""),
    (re.compile(r"\bgod\b", re.IGNORECASE), ""),
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sanitize selected religious terms inside a League stringtable JSON file."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=r"D:\Games Installation\lol.stringtable.json",
        help="Path to the source JSON file.",
    )
    parser.add_argument(
        "--output",
        help="Optional output path. If omitted, the input file is updated in place.",
    )
    return parser.parse_args()


def preserve_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source.islower():
        return replacement.lower()
    if source[0].isupper() and source[1:].islower():
        return replacement.title()
    return replacement


def replace_text(text: str):
    changed = False
    for pattern, replacement in REPLACEMENTS:
        def repl(match):
            if replacement:
                return preserve_case(match.group(0), replacement)
            return ""

        new_text, count = pattern.subn(repl, text)
        if count:
            changed = True
            text = new_text
    return text, changed


def normalize_value(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def cleanup_removed_terms(text: str) -> str:
    # Trim whitespace left behind when standalone words are removed.
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\(\s+\)", "", text)
    text = re.sub(r"\[\s+\]", "", text)
    text = re.sub(r"\{\s+\}", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([(/-])\s+", r"\1", text)
    text = re.sub(r"\s+([)/-])", r"\1", text)
    return text.strip()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict) or "entries" not in data or not isinstance(data["entries"], dict):
        raise ValueError("Expected a top-level object with an 'entries' dictionary.")

    changed_entries = 0
    replacement_hits = 0
    updated_entries = {}

    for key, value in data["entries"].items():
        text = normalize_value(value)
        new_text = text
        changed = False

        for pattern, replacement in REPLACEMENTS:
            def repl(match):
                if replacement:
                    return preserve_case(match.group(0), replacement)
                return ""

            new_text, count = pattern.subn(repl, new_text)
            if count:
                replacement_hits += count
                changed = True

        if changed:
            new_text = cleanup_removed_terms(new_text)

        if changed:
            changed_entries += 1

        updated_entries[key] = new_text

    data["entries"] = updated_entries

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))

    print(f"Updated {changed_entries} entries with {replacement_hits} replacements.")
    print(f"Wrote sanitized JSON to {output_path}")


if __name__ == "__main__":
    main()
