import json
from pathlib import Path


def load_golden_queries() -> list[dict]:
    queries_path = Path(__file__).parent / "golden_queries.json"
    with queries_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run_eval(query: dict) -> dict:
    return {"passed": False, "reason": "not implemented"}


def main() -> None:
    load_golden_queries()
    print("Eval runner not yet wired to agent — scaffold only")


if __name__ == "__main__":
    main()
