"""Export a sealed tape to an OTLP JSONL file without executing its producer."""
import argparse
import json
from pathlib import Path
from investigator.tape_trace import convert, footer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tape', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    trace, summary = convert(args.tape)
    # Never overwrite evidence or an earlier export.
    with args.output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(trace, separators=(',', ':'), ensure_ascii=False) + '\n')
    print(json.dumps(summary, sort_keys=True))
    print(footer(summary))


if __name__ == '__main__': main()
