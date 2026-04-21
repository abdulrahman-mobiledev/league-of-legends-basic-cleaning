import argparse
import json
import struct
from pathlib import Path

from xxhash import xxh3_64_intdigest


DEFAULT_VERSION = 5
V5_HASH_BITS = 38
V5_REF_BITS = 39


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a League of Legends .stringtable.json file back into .stringtable format."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=r"D:\Games Installation\lol.stringtable.json",
        help="Path to the input JSON file.",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=r"D:\Games Installation\lol.stringtable.rebuilt",
        help="Path to the output .stringtable file.",
    )
    return parser.parse_args()


def load_entries(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, dict) and "entries" in data:
        entries = data["entries"]
        version = int(data.get("version", DEFAULT_VERSION))
    elif isinstance(data, dict):
        entries = data
        version = DEFAULT_VERSION
    else:
        raise ValueError("Expected a JSON object at the top level.")

    if not isinstance(entries, dict):
        raise ValueError("Expected 'entries' to be a JSON object.")

    return version, entries


def normalize_value(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def key_to_hash_v5(key: str) -> int:
    if key.startswith("{") and key.endswith("}"):
        return int(key[1:-1], 16)
    return xxh3_64_intdigest(key.lower()) & ((1 << V5_HASH_BITS) - 1)


def build_v5_entries(entries):
    built = []

    for key, value in entries.items():
        hash_value = key_to_hash_v5(key)
        if hash_value >= (1 << V5_HASH_BITS):
            raise ValueError(
                f"Key {key!r} produced hash {hash_value:#x}, which does not fit in {V5_HASH_BITS} bits."
            )

        text = normalize_value(value).encode("utf-8") + b"\0"
        built.append((hash_value, text, key))

    built.sort(key=lambda item: item[0])

    # Version 5 uses 38 hash bits and stores the string offset low bit in bit 38
    # of the 39-bit reference field. The remaining upper bits store offset >> 1.
    offset = 0
    refs = []
    data_chunks = []
    seen_hashes = set()
    value_offsets = {}

    for hash_value, text, key in built:
        if hash_value in seen_hashes:
            raise ValueError(f"Duplicate hash collision for key {key!r} ({hash_value:#x}).")
        seen_hashes.add(hash_value)

        if text in value_offsets:
            offset_for_value = value_offsets[text]
        else:
            offset_for_value = offset
            value_offsets[text] = offset_for_value
            data_chunks.append(text)
            offset += len(text)

        parity_bit = offset_for_value & 1
        ref = ((offset_for_value >> 1) << V5_REF_BITS) | (parity_bit << V5_HASH_BITS) | hash_value
        refs.append(ref)

    return refs, b"".join(data_chunks)


def write_v5(output_path: Path, refs, entry_blob: bytes):
    with output_path.open("wb") as handle:
        handle.write(b"RST")
        handle.write(struct.pack("<B", 5))
        handle.write(struct.pack("<L", len(refs)))
        for ref in refs:
            handle.write(struct.pack("<Q", ref))
        handle.write(entry_blob)


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    print(f"Loading JSON from {input_path}...")
    version, entries = load_entries(input_path)
    print(f"Loaded {len(entries)} entries (version {version})")

    if version != 5:
        raise ValueError(
            f"This converter currently supports version 5 JSON files. Found version {version}."
        )

    refs, entry_blob = build_v5_entries(entries)

    print(f"Writing stringtable to {output_path}...")
    write_v5(output_path, refs, entry_blob)
    print("Conversion completed!")


if __name__ == "__main__":
    main()
