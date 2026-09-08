"""Check runtime, Blender, FFmpeg, bridge permissions, and unresolved requests."""

import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from protocol_common import TERMINAL_STATES, read_json


def find_blender():
    found = []
    configured = os.environ.get("BLENDER_EXE")
    if configured and Path(configured).is_file():
        found.append(str(Path(configured).resolve()))
    direct = shutil.which("blender")
    if direct:
        found.append(str(Path(direct).resolve()))
    if os.name == "nt":
        roots = [Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Blender Foundation"]
        for root in roots:
            if root.exists():
                found.extend(str(path.resolve()) for path in root.glob("Blender */blender.exe"))
    elif sys.platform == "darwin":
        candidate = Path("/Applications/Blender.app/Contents/MacOS/Blender")
        if candidate.exists():
            found.append(str(candidate))
    return sorted(set(found))


def is_network_path(path):
    value = str(path)
    if value.startswith("\\\\"):
        return True
    if os.name != "nt":
        return False
    try:
        anchor = Path(path).anchor
        return bool(anchor) and ctypes.windll.kernel32.GetDriveTypeW(str(anchor)) == 4
    except Exception:
        return False


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, TypeError, ValueError):
        return False


def process_probe():
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq blender.exe", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=5,
            )
            return {"ok": result.returncode == 0, "output": result.stdout.strip()}
        result = subprocess.run(["pgrep", "-a", "blender"], capture_output=True, text=True, timeout=5)
        return {"ok": result.returncode in (0, 1), "output": result.stdout.strip()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def inspect_bridge(root):
    if root is None:
        return None
    root = root.resolve()
    writable = False
    write_error = None
    if root.exists():
        try:
            with tempfile.NamedTemporaryFile(prefix="doctor-", dir=root, delete=True):
                writable = True
        except OSError as exc:
            write_error = str(exc)
    states = []
    for path in sorted((root / "states").glob("*.json")) if root.exists() else []:
        state = read_json(path, {}) or {}
        if state.get("state") not in TERMINAL_STATES:
            states.append({"id": path.stem, "state": state.get("state"), "updated_at": state.get("updated_at")})
    inflight = read_json(root / "inflight.json") if root.exists() else None
    client_lock = read_json(root / "client.lock") if root.exists() else None
    if isinstance(client_lock, dict):
        client_lock["pid_alive"] = pid_alive(client_lock.get("pid"))
    heartbeat = read_json(root / "heartbeat.json") if root.exists() else None
    heartbeat_age = time.time() - heartbeat.get("timestamp", 0) if isinstance(heartbeat, dict) else None
    lowered = str(root).lower()
    sync_warning = any(label in lowered for label in ("onedrive", "dropbox", "google drive", "icloud"))
    return {
        "path": str(root),
        "exists": root.exists(),
        "writable": writable,
        "write_error": write_error,
        "network_share": is_network_path(root),
        "sync_directory_warning": sync_warning,
        "mode": oct(root.stat().st_mode & 0o777) if root.exists() else None,
        "group_or_world_writable": bool(root.exists() and os.name != "nt" and root.stat().st_mode & 0o022),
        "protocol": (read_json(root / "bridge_config.json", {}) or {}).get("protocol"),
        "heartbeat_age_seconds": heartbeat_age,
        "inflight": inflight,
        "client_lock": client_lock,
        "stopped": read_json(root / "stopped.json") if root.exists() else None,
        "unresolved_states": states,
        "queued_files": len(list((root / "requests").glob("*.json"))) if root.exists() else 0,
        "response_files": len(list((root / "responses").glob("*.json"))) if root.exists() else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-dir")
    args = parser.parse_args()
    bridge = Path(args.bridge_dir) if args.bridge_dir else None
    payload = {
        "python": {"executable": sys.executable, "version": sys.version.split()[0]},
        "blender_executables": find_blender(),
        "blender_processes": process_probe(),
        "ffmpeg": shutil.which("ffmpeg"),
        "bridge": inspect_bridge(bridge),
    }
    problems = []
    warnings = []
    if not payload["blender_executables"]:
        problems.append("Blender executable was not found in PATH or common install locations")
    if not payload["ffmpeg"]:
        warnings.append("FFmpeg was not found; PNG review frames still work, video/contact-sheet helpers do not")
    if payload["bridge"]:
        info = payload["bridge"]
        if info["network_share"] or info["sync_directory_warning"]:
            problems.append("Bridge path is not an appropriate private local directory")
        if info["exists"] and not info["writable"]:
            problems.append("Bridge directory is not writable")
        if info["group_or_world_writable"]:
            problems.append("Bridge directory is writable by group or other users")
        if isinstance(info["client_lock"], dict):
            problems.append("Bridge has a client lock; inspect its PID before removing a stale lock")
        if info["inflight"] or info["unresolved_states"] or info["queued_files"]:
            problems.append("Bridge has unresolved work; inspect status before submitting or starting another instance")
    payload["problems"] = problems
    payload["warnings"] = warnings
    payload["ok"] = not problems
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
