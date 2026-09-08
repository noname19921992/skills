"""Request cancellation; only queued or accepted requests are guaranteed cancellable."""

import argparse
import json
import os
import time
from pathlib import Path

from protocol_common import (
    TERMINAL_STATES,
    PROTOCOL_VERSION,
    atomic_write_json,
    read_json,
    valid_request_id,
    write_state,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-dir", required=True)
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    if not valid_request_id(args.request_id):
        raise SystemExit("--request-id must be a canonical UUID")
    root = Path(args.bridge_dir).resolve()
    config = read_json(root / "bridge_config.json", {}) or {}
    token = config.get("token")
    if config.get("protocol") != PROTOCOL_VERSION or not isinstance(token, str) or not token:
        raise SystemExit("Valid protocol-v2 bridge_config.json is required")
    state = read_json(root / "states" / f"{args.request_id}.json", {}) or {}
    current = state.get("state")
    if current in TERMINAL_STATES:
        print(json.dumps({"id": args.request_id, "state": current, "changed": False}, indent=2))
        return 0
    marker = {
        "id": args.request_id,
        "token": token,
        "requested_at": time.time(),
        "observed_state": current,
        "guaranteed": False,
    }
    atomic_write_json(root / "cancellations" / f"{args.request_id}.json", marker)

    # Atomically claim a still-queued request. Whichever side moves requests/<id>.json
    # first owns it: this client cancels it, or Blender accepts it for execution.
    request_path = root / "requests" / f"{args.request_id}.json"
    cancelled_path = root / "archive" / "cancelled_requests" / f"{args.request_id}.json"
    cancelled_path.parent.mkdir(parents=True, exist_ok=True)
    if current == "queued" and request_path.exists():
        try:
            os.replace(request_path, cancelled_path)
        except FileNotFoundError:
            pass
        else:
            marker.update({"guaranteed": True, "cancelled_at": time.time(),
                           "archived_request": str(cancelled_path)})
            atomic_write_json(root / "cancellations" / f"{args.request_id}.json", marker)
            write_state(root, args.request_id, "cancelled", reason="cancelled_while_queued",
                        archived_request=str(cancelled_path))
            atomic_write_json(root / "responses" / f"{args.request_id}.json", {
                "protocol": PROTOCOL_VERSION,
                "id": args.request_id,
                "state": "cancelled",
                "ok": False,
                "finished_at": time.time(),
                "result": {"cancelled_before_acceptance": True},
                "error": None,
            })
    print(json.dumps(marker, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
