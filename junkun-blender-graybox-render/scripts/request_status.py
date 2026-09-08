"""Read the durable status and response for one bridge request."""

import argparse
import json
from pathlib import Path

from protocol_common import read_json, valid_request_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-dir", required=True)
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    root = Path(args.bridge_dir).resolve()
    request_id = args.request_id
    if not valid_request_id(request_id):
        raise SystemExit("--request-id must be a canonical UUID")
    state = read_json(root / "states" / f"{request_id}.json")
    response = read_json(root / "responses" / f"{request_id}.json")
    inflight = read_json(root / "inflight.json")
    cancellation = read_json(root / "cancellations" / f"{request_id}.json")
    payload = {
        "id": request_id,
        "state": state,
        "response": response,
        "is_inflight": isinstance(inflight, dict) and inflight.get("id") == request_id,
        "inflight": inflight if isinstance(inflight, dict) and inflight.get("id") == request_id else None,
        "cancellation": cancellation,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if state or response else 1


if __name__ == "__main__":
    raise SystemExit(main())
