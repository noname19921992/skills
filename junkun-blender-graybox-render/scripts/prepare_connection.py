"""Create a private protocol-v2 bridge directory without starting Blender."""

import argparse
import ctypes
import json
import os
import secrets
from pathlib import Path

from protocol_common import PROTOCOL_VERSION, atomic_write_json


def is_network_path(path: Path) -> bool:
    if str(path).startswith("\\\\"):
        return True
    if os.name != "nt":
        return False
    try:
        return bool(path.anchor) and ctypes.windll.kernel32.GetDriveTypeW(path.anchor) == 4
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-dir", required=True)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    root = Path(args.bridge_dir).resolve()
    project = Path(args.project_dir).resolve()
    if is_network_path(root):
        raise SystemExit("Network-share bridge directories are not supported")
    if any(label in str(root).lower() for label in ("onedrive", "dropbox", "google drive", "icloud")):
        raise SystemExit("Bridge directories inside common sync roots are not supported")
    if root.exists() and any(root.iterdir()):
        raise SystemExit("Directory is not empty. Inspect it or choose a fresh bridge directory.")

    template = Path(__file__).resolve().parents[1] / "assets" / "blender_file_bridge.py"
    source = template.read_text(encoding="utf-8")
    token = secrets.token_urlsafe(32)
    replacements = {
        "BRIDGE_ROOT = None": "BRIDGE_ROOT = Path(" + repr(str(root)) + ")",
        "BRIDGE_TOKEN = None": "BRIDGE_TOKEN = " + repr(token),
        "PROJECT_ROOT = None": "PROJECT_ROOT = Path(" + repr(str(project)) + ")",
    }
    for marker, replacement in replacements.items():
        if source.count(marker) != 1:
            raise SystemExit("Unexpected bridge template marker: " + marker)
        source = source.replace(marker, replacement, 1)

    directories = [
        root / "requests", root / "archive" / "requests", root / "states",
        root / "state_history", root / "responses", root / "cancellations",
        root / "archive" / "cancelled_requests", root / "backups", root / "logs",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except OSError:
        pass
    bridge_script = root / "bridge.py"
    bridge_script.write_text(source, encoding="utf-8")
    config = {
        "protocol": PROTOCOL_VERSION,
        "bridge_dir": str(root),
        "project_dir": str(project),
        "token": token,
        "security": "trusted-local-single-user",
    }
    atomic_write_json(root / "bridge_config.json", config)
    try:
        os.chmod(bridge_script, 0o600)
        os.chmod(root / "bridge_config.json", 0o600)
    except OSError:
        pass
    print(json.dumps({
        "protocol": PROTOCOL_VERSION,
        "bridge": str(bridge_script),
        "config": str(root / "bridge_config.json"),
        "status": "prepared_not_connected",
        "warning": "Keep the bridge directory private; it carries trusted local execution requests.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
