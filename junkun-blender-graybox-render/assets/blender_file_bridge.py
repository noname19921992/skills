"""Run inside Blender: durable local file bridge protocol v2."""

import hashlib
import json
import os
import time
import traceback
import uuid
from pathlib import Path

import bpy

BRIDGE_ROOT = None
BRIDGE_TOKEN = None
PROJECT_ROOT = None
if BRIDGE_ROOT is None or BRIDGE_TOKEN is None:
    raise RuntimeError("Run scripts/prepare_connection.py and use its generated bridge.py")

PROTOCOL = 2
ROOT = Path(BRIDGE_ROOT)
REQUESTS = ROOT / "requests"
ARCHIVE = ROOT / "archive" / "requests"
STATES = ROOT / "states"
STATE_HISTORY = ROOT / "state_history"
RESPONSES = ROOT / "responses"
CANCELLATIONS = ROOT / "cancellations"
CANCELLED_ARCHIVE = ROOT / "archive" / "cancelled_requests"
BACKUPS = ROOT / "backups"
INFLIGHT = ROOT / "inflight.json"
CONNECTED = ROOT / "connected.json"
HEARTBEAT = ROOT / "heartbeat.json"
TERMINAL = {"completed", "failed", "cancelled"}
TRANSITIONS = {
    None: {"failed"},
    "queued": {"accepted", "failed", "cancelled"},
    "accepted": {"running", "failed", "cancelled"},
    "running": {"completed", "failed"},
}
OPERATIONS = {
    "inspect_scene",
    "save_copy",
    "upsert_camera",
    "render_review_frames",
    "export_shot_manifest",
}
MUTATING_OPERATIONS = {"upsert_camera"}
_last_heartbeat = 0.0


def atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    os.replace(temp, path)


def read_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_state(request_id, state, **extra):
    current = read_json(STATES / (request_id + ".json"), {}) or {}
    previous = current.get("state")
    if state != previous and state not in TRANSITIONS.get(previous, set()):
        raise RuntimeError("Invalid state transition: %r -> %r" % (previous, state))
    payload = {
        "protocol": PROTOCOL,
        "id": request_id,
        "state": state,
        "previous_state": previous,
        "updated_at": time.time(),
        **extra,
    }
    atomic_json(STATES / (request_id + ".json"), payload)
    STATE_HISTORY.mkdir(parents=True, exist_ok=True)
    with (STATE_HISTORY / (request_id + ".jsonl")).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
    return payload


def final_response(request_id, state, result=None, error=None, **extra):
    payload = {
        "protocol": PROTOCOL,
        "id": request_id,
        "state": state,
        "ok": state == "completed",
        "finished_at": time.time(),
        "result": result,
        "error": error,
        **extra,
    }
    atomic_json(RESPONSES / (request_id + ".json"), payload)
    write_state(request_id, state, response=str(RESPONSES / (request_id + ".json")))
    return payload


def validate_request(path, request):
    if not isinstance(request, dict):
        raise ValueError("Request must be a JSON object")
    request_id = request.get("id")
    try:
        parsed = str(uuid.UUID(request_id))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Invalid request id") from exc
    if parsed != path.stem.lower():
        raise ValueError("Request id does not match filename")
    if request.get("protocol") != PROTOCOL:
        raise ValueError("Unsupported protocol")
    if request.get("token") != BRIDGE_TOKEN:
        raise ValueError("Bridge token mismatch")
    if not isinstance(request.get("created_at"), (int, float)):
        raise ValueError("created_at is required")
    if not isinstance(request.get("expires_at"), (int, float)):
        raise ValueError("expires_at is required")
    if request["expires_at"] <= time.time():
        raise TimeoutError("Request expired before execution")
    kind = request.get("kind")
    if kind == "operation":
        if request.get("operation") not in OPERATIONS:
            raise ValueError("Unsupported structured operation")
        if not isinstance(request.get("args"), dict):
            raise ValueError("Operation args must be an object")
    elif kind == "code":
        code = request.get("code")
        digest = request.get("code_sha256")
        if request.get("high_risk") is not True or not isinstance(code, str):
            raise ValueError("Arbitrary code must be explicitly high risk")
        actual = hashlib.sha256(code.encode("utf-8")).hexdigest()
        if digest != actual:
            raise ValueError("Code SHA-256 mismatch")
    else:
        raise ValueError("Unknown request kind")
    return request_id


def valid_cancellation(request_id):
    marker = read_json(CANCELLATIONS / (request_id + ".json"), {}) or {}
    return marker if marker.get("id") == request_id and marker.get("token") == BRIDGE_TOKEN else None


def scene_for(args):
    name = args.get("scene")
    if name:
        scene = bpy.data.scenes.get(name)
        if scene is None:
            raise ValueError("Scene not found: " + str(name))
        return scene
    return bpy.context.scene


def inspect_scene(args):
    scene = scene_for(args)
    offset = max(0, int(args.get("offset", 0)))
    limit = max(1, min(500, int(args.get("limit", 200))))
    objects = sorted(scene.objects, key=lambda item: item.name)
    page = objects[offset:offset + limit]
    return {
        "version": bpy.app.version_string,
        "pid": os.getpid(),
        "file": bpy.data.filepath,
        "active_scene": scene.name,
        "scene_names": [item.name for item in bpy.data.scenes],
        "object_count": len(objects),
        "objects_offset": offset,
        "objects_limit": limit,
        "objects": [{
            "name": item.name,
            "type": item.type,
            "collection_names": [collection.name for collection in item.users_collection],
            "hidden_viewport": item.hide_viewport,
            "hidden_render": item.hide_render,
        } for item in page],
        "collections": [item.name for item in scene.collection.children],
        "camera": scene.camera.name if scene.camera else None,
        "cameras": [{"name": item.name, "lens_mm": item.data.lens}
                    for item in objects if item.type == "CAMERA"],
        "frames": [scene.frame_start, scene.frame_end],
        "current_frame": scene.frame_current,
        "fps": scene.render.fps / scene.render.fps_base,
        "units": scene.unit_settings.system,
        "render_engine": scene.render.engine,
    }


def save_copy(args):
    raw = args.get("filepath")
    if not raw:
        raise ValueError("save_copy requires filepath")
    target = Path(raw).expanduser().resolve()
    if target.suffix.lower() != ".blend":
        target = target.with_suffix(".blend")
    target.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(target), copy=True, check_existing=False)
    if not target.exists():
        raise RuntimeError("Blender did not create the requested copy")
    return {"filepath": str(target), "bytes": target.stat().st_size}


def vector3(value, label):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(label + " must contain three numbers")
    return tuple(float(item) for item in value)


def upsert_camera(args):
    scene = scene_for(args)
    name = str(args.get("name") or "JUNKUN_CAMERA")
    camera = bpy.data.objects.get(name)
    created = camera is None
    if camera is not None and camera.type != "CAMERA":
        raise ValueError("Object exists but is not a camera: " + name)
    if camera is None:
        data = bpy.data.cameras.new(name + "_DATA")
        camera = bpy.data.objects.new(name, data)
        scene.collection.objects.link(camera)
    if "location" in args:
        camera.location = vector3(args["location"], "location")
    if "lens_mm" in args:
        camera.data.lens = float(args["lens_mm"])

    for key in ("clip_start", "clip_end", "sensor_width"):
        if key in args:
            setattr(camera.data, key, float(args[key]))

    use_target = bool(args.get("use_target", True))
    target = None
    constraint = camera.constraints.get("JUNKUN_TRACK_TO")
    if use_target:
        target_name = str(args.get("target_name") or name + "_TARGET")
        target = bpy.data.objects.get(target_name)
        if target is not None and target.type != "EMPTY":
            raise ValueError("Target exists but is not an Empty: " + target_name)
        if target is None:
            target = bpy.data.objects.new(target_name, None)
            target.empty_display_type = "SPHERE"
            target.empty_display_size = 0.25
            scene.collection.objects.link(target)
        if "target_location" in args:
            target.location = vector3(args["target_location"], "target_location")
        if constraint is None:
            constraint = camera.constraints.new(type="TRACK_TO")
            constraint.name = "JUNKUN_TRACK_TO"
        constraint.target = target
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"
    else:
        if constraint is not None:
            camera.constraints.remove(constraint)
        if "rotation_euler" in args:
            camera.rotation_euler = vector3(args["rotation_euler"], "rotation_euler")
    if args.get("make_active", True):
        scene.camera = camera

    for key in ("shot_name", "shot_purpose", "camera_move", "subject"):
        if key in args:
            camera[key] = str(args[key])
    marker_name = None
    if "start_frame" in args:
        marker_name = str(args.get("marker_name") or args.get("shot_name") or name)
        marker = next((item for item in scene.timeline_markers if item.name == marker_name), None)
        if marker is None:
            marker = scene.timeline_markers.new(marker_name, frame=int(args["start_frame"]))
        else:
            marker.frame = int(args["start_frame"])
        marker.camera = camera
    if "end_frame" in args:
        camera["shot_end_frame"] = int(args["end_frame"])
    for beat in args.get("keyframes", []):
        frame = int(beat["frame"])
        if "location" in beat:
            camera.location = vector3(beat["location"], "keyframe location")
            camera.keyframe_insert(data_path="location", frame=frame)
        if target is not None and "target_location" in beat:
            target.location = vector3(beat["target_location"], "keyframe target_location")
            target.keyframe_insert(data_path="location", frame=frame)
        if target is None and "rotation_euler" in beat:
            camera.rotation_euler = vector3(beat["rotation_euler"], "keyframe rotation_euler")
            camera.keyframe_insert(data_path="rotation_euler", frame=frame)
        if "lens_mm" in beat:
            camera.data.lens = float(beat["lens_mm"])
            camera.data.keyframe_insert(data_path="lens", frame=frame)
    return {"camera": camera.name, "target": target.name if target else None, "created": created,
            "lens_mm": camera.data.lens, "scene": scene.name, "marker": marker_name}


def render_review_frames(args):
    scene = scene_for(args)
    frames = [int(item) for item in args.get("frames", [])]
    if not frames or len(frames) > 500:
        raise ValueError("frames must contain 1 to 500 frame numbers")
    output_dir = Path(args.get("output_dir", "")).expanduser().resolve()
    if not str(args.get("output_dir", "")).strip():
        raise ValueError("output_dir is required")
    output_dir.mkdir(parents=True, exist_ok=True)
    old = {
        "frame": scene.frame_current,
        "filepath": scene.render.filepath,
        "resolution_x": scene.render.resolution_x,
        "resolution_y": scene.render.resolution_y,
        "resolution_percentage": scene.render.resolution_percentage,
        "format": scene.render.image_settings.file_format,
        "engine": scene.render.engine,
    }
    outputs = []
    warning = None
    try:
        scene.render.resolution_x = int(args.get("resolution_x", 1280))
        scene.render.resolution_y = int(args.get("resolution_y", 720))
        scene.render.resolution_percentage = int(args.get("resolution_percentage", 100))
        scene.render.image_settings.file_format = "PNG"
        requested_engine = args.get("engine")
        if requested_engine:
            try:
                scene.render.engine = requested_engine
            except Exception:
                warning = "Requested render engine unavailable; retained " + old["engine"]
        for index, frame in enumerate(frames, 1):
            scene.frame_set(frame)
            target = output_dir / ("review_%04d_f%06d.png" % (index, frame))
            scene.render.filepath = str(target)
            bpy.ops.render.render(write_still=True, scene=scene.name)
            outputs.append({"frame": frame, "filepath": str(target), "exists": target.exists()})
    finally:
        scene.frame_set(old["frame"])
        scene.render.filepath = old["filepath"]
        scene.render.resolution_x = old["resolution_x"]
        scene.render.resolution_y = old["resolution_y"]
        scene.render.resolution_percentage = old["resolution_percentage"]
        scene.render.image_settings.file_format = old["format"]
        scene.render.engine = old["engine"]
    return {"scene": scene.name, "outputs": outputs, "warning": warning}


def export_shot_manifest(args):
    scene = scene_for(args)
    raw = args.get("filepath")
    if not raw:
        raise ValueError("export_shot_manifest requires filepath")
    target = Path(raw).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    markers = sorted([item for item in scene.timeline_markers if item.camera], key=lambda item: item.frame)
    shots = []
    for index, marker in enumerate(markers):
        camera = marker.camera
        default_end = markers[index + 1].frame - 1 if index + 1 < len(markers) else scene.frame_end
        end = int(camera.get("shot_end_frame", default_end))
        shots.append({
            "name": camera.get("shot_name", marker.name),
            "start": marker.frame,
            "end": end,
            "camera": camera.name,
            "purpose": camera.get("shot_purpose", ""),
            "lens_mm": camera.data.lens,
            "camera_move": camera.get("camera_move", ""),
            "subject": camera.get("subject", ""),
        })
    payload = {"scene": scene.name, "fps": scene.render.fps / scene.render.fps_base, "shots": shots}
    atomic_json(target, payload)
    return {"filepath": str(target), "shot_count": len(shots), "manifest": payload}


OPERATION_HANDLERS = {
    "inspect_scene": inspect_scene,
    "save_copy": save_copy,
    "upsert_camera": upsert_camera,
    "render_review_frames": render_review_frames,
    "export_shot_manifest": export_shot_manifest,
}


def safety_checkpoint(request_id):
    BACKUPS.mkdir(parents=True, exist_ok=True)
    source_name = Path(bpy.data.filepath).stem if bpy.data.filepath else "unsaved"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    target = BACKUPS / (source_name + "_before_" + stamp + "_" + request_id[:8] + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(target), copy=True, check_existing=False)
    if not target.exists():
        raise RuntimeError("Safety backup was not created; mutation aborted")
    undo = {"created": False, "error": None}
    try:
        bpy.ops.ed.undo_push(message="Junkun request " + request_id)
        undo["created"] = True
    except Exception as exc:
        undo["error"] = str(exc)
    return {"backup": str(target), "undo_checkpoint": undo}


def execute_request(request):
    if request["kind"] == "operation":
        return OPERATION_HANDLERS[request["operation"]](request.get("args") or {})
    scope = {"bpy": bpy, "result": None, "__name__": "__junkun_blender_request__"}
    exec(compile(request["code"], "<junkun-blender-high-risk-request>", "exec"), scope)
    return scope.get("result")


def handle_request(path):
    raw_id = path.stem.lower()
    archive_path = ARCHIVE / path.name
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        path.unlink(missing_ok=True)
        try:
            final_response(raw_id, "failed", error="Archived request id already exists; request rejected")
        except Exception:
            pass
        return
    try:
        os.replace(path, archive_path)
    except FileNotFoundError:
        return
    except Exception:
        return

    request = read_json(archive_path)

    try:
        request_id = validate_request(archive_path, request)
    except TimeoutError:
        try:
            final_response(raw_id, "cancelled", result={"reason": "expired_before_execution"},
                           archived_request=str(archive_path))
        except Exception:
            pass
        return
    except Exception:
        try:
            final_response(raw_id, "failed", error=traceback.format_exc(), archived_request=str(archive_path))
        except Exception:
            pass
        return

    try:
        write_state(request_id, "accepted", archived_request=str(archive_path))
        atomic_json(INFLIGHT, {"protocol": PROTOCOL, "id": request_id, "state": "accepted",
                               "pid": os.getpid(), "updated_at": time.time()})
        if valid_cancellation(request_id):
            final_response(request_id, "cancelled", result={"cancelled_before_running": True})
            return
        write_state(request_id, "running")
        atomic_json(INFLIGHT, {"protocol": PROTOCOL, "id": request_id, "state": "running",
                               "pid": os.getpid(), "started_at": time.time()})
        preflight = None
        if request["kind"] == "code" or request.get("operation") in MUTATING_OPERATIONS:
            preflight = safety_checkpoint(request_id)
        result = execute_request(request)
        final_response(request_id, "completed", result=result, preflight=preflight,
                       cancel_requested=bool(valid_cancellation(request_id)))
    except Exception:
        try:
            final_response(request_id, "failed", error=traceback.format_exc())
        except Exception:
            pass
    finally:
        current = read_json(INFLIGHT, {}) or {}
        if current.get("id") == request_id:
            INFLIGHT.unlink(missing_ok=True)


def poll():
    global _last_heartbeat
    now = time.time()
    if now - _last_heartbeat >= 2.0:
        atomic_json(HEARTBEAT, {"protocol": PROTOCOL, "pid": os.getpid(), "timestamp": now,
                                "file": bpy.data.filepath})
        _last_heartbeat = now
    if INFLIGHT.exists():
        return 0.25
    candidates = sorted(REQUESTS.glob("*.json"), key=lambda item: item.stat().st_mtime)
    if candidates:
        handle_request(candidates[0])
    return 0.25


for directory in (REQUESTS, ARCHIVE, CANCELLED_ARCHIVE, STATES, STATE_HISTORY, RESPONSES,
                  CANCELLATIONS, BACKUPS, ROOT / "logs"):
    directory.mkdir(parents=True, exist_ok=True)
old = bpy.app.driver_namespace.get("_junkun_blender_clay_bridge")
if old and bpy.app.timers.is_registered(old):
    bpy.app.timers.unregister(old)
bpy.app.driver_namespace["_junkun_blender_clay_bridge"] = poll
bpy.app.timers.register(poll, first_interval=0.1, persistent=True)
atomic_json(CONNECTED, {
    "protocol": PROTOCOL,
    "version": bpy.app.version_string,
    "file": bpy.data.filepath,
    "timestamp": time.time(),
    "pid": os.getpid(),
    "executable": bpy.app.binary_path,
    "project_root": PROJECT_ROOT,
})
