"""Start a controlled interactive Blender instance and verify protocol v2."""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

from protocol_common import atomic_write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--timeout", type=float, default=45.0)
    args = parser.parse_args()
    executable = Path(args.blender).resolve()
    if not executable.is_file():
        raise SystemExit("Blender executable not found")
    project = Path(args.project_dir).resolve()
    project.mkdir(parents=True, exist_ok=True)
    scripts = Path(__file__).resolve().parent
    bridge = project / ("junkun_blender_connection_" + uuid.uuid4().hex[:12])
    subprocess.run([
        sys.executable, str(scripts / "prepare_connection.py"),
        "--bridge-dir", str(bridge), "--project-dir", str(project),
    ], check=True, capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    log_path = bridge / "logs" / "startup.log"
    with log_path.open("wb") as log:
        process = subprocess.Popen(
            [str(executable), "--python", str(bridge / "bridge.py")],
            stdout=log, stderr=subprocess.STDOUT,
        )
    atomic_write_json(bridge / "launch.json", {
        "pid": process.pid,
        "executable": str(executable),
        "timestamp": time.time(),
        "mode": "new_controlled_interactive_instance",
    })

    deadline = time.monotonic() + args.timeout
    while not (bridge / "connected.json").exists():
        if process.poll() is not None or time.monotonic() >= deadline:
            raise SystemExit(f"Startup not verified. Inspect {log_path} and {bridge}; do not launch again blindly.")
        time.sleep(0.2)

    inspection = subprocess.run([
        sys.executable, str(scripts / "send_blender_request.py"),
        "--bridge-dir", str(bridge), "--operation", "inspect_scene",
        "--args-json", '{"offset": 0, "limit": 100}', "--timeout", "15",
    ], capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    stdout = inspection.stdout.decode("utf-8", errors="replace")
    if inspection.returncode:
        raise SystemExit(f"Inspection failed. Inspect {bridge}; do not retry blindly.\n{stdout}\n" +
                         inspection.stderr.decode("utf-8", errors="replace"))
    response = json.loads(stdout)
    if response.get("state") != "completed" or not response.get("id"):
        raise SystemExit("Invalid inspection response: " + str(bridge))

    connection = {
        "protocol": 2,
        "bridge_dir": str(bridge),
        "pid": process.pid,
        "mode": "new_controlled_interactive_instance",
        "verified_request_id": response["id"],
        "inspection": response.get("result"),
    }
    atomic_write_json(project / "blender_active_connection.json", connection)
    print(json.dumps(connection, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

