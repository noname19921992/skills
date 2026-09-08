"""Installable Blender Add-on for attaching protocol v2 to an existing window."""

bl_info = {
    "name": "Junkun Blender Clay Bridge",
    "author": "Junkun",
    "version": (2, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Junkun",
    "description": "Attach a prepared private file bridge to the current Blender instance",
    "category": "System",
}

import json
import runpy
import time
from pathlib import Path

import bpy
from bpy.props import StringProperty


class JUNKUNBRIDGE_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    bridge_dir: StringProperty(name="Prepared bridge directory", subtype="DIR_PATH")

    def draw(self, context):
        self.layout.prop(self, "bridge_dir")


def preferences(context):
    return context.preferences.addons[__name__].preferences


class JUNKUNBRIDGE_OT_Start(bpy.types.Operator):
    bl_idname = "junkun_bridge.start"
    bl_label = "Start Trusted Local Bridge"
    bl_description = "Run bridge.py from the prepared private directory"

    def execute(self, context):
        raw = preferences(context).bridge_dir
        root = Path(bpy.path.abspath(raw)).expanduser().resolve()
        script = root / "bridge.py"
        config = root / "bridge_config.json"
        if not script.is_file() or not config.is_file():
            self.report({"ERROR"}, "Run prepare_connection.py first and select that directory")
            return {"CANCELLED"}
        try:
            payload = json.loads(config.read_text(encoding="utf-8"))
            if payload.get("protocol") != 2:
                raise ValueError("protocol v2 is required")
            runpy.run_path(str(script), run_name="__junkun_blender_bridge_boot__")
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, "Junkun bridge started")
        return {"FINISHED"}


class JUNKUNBRIDGE_OT_Stop(bpy.types.Operator):
    bl_idname = "junkun_bridge.stop"
    bl_label = "Stop Bridge"

    def execute(self, context):
        poll = bpy.app.driver_namespace.pop("_junkun_blender_clay_bridge", None)
        if poll and bpy.app.timers.is_registered(poll):
            bpy.app.timers.unregister(poll)
        raw = preferences(context).bridge_dir
        if raw:
            try:
                root = Path(bpy.path.abspath(raw)).expanduser().resolve()
                (root / "stopped.json").write_text(json.dumps({
                    "pid": __import__("os").getpid(), "timestamp": time.time(), "reason": "stopped_from_addon"
                }), encoding="utf-8")
            except Exception:
                pass
        self.report({"INFO"}, "Junkun bridge stopped")
        return {"FINISHED"}


class JUNKUNBRIDGE_PT_Panel(bpy.types.Panel):
    bl_label = "Junkun Clay Bridge"
    bl_idname = "JUNKUNBRIDGE_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Junkun"

    def draw(self, context):
        layout = self.layout
        layout.prop(preferences(context), "bridge_dir")
        running = bpy.app.driver_namespace.get("_junkun_blender_clay_bridge") is not None
        layout.label(text="Running" if running else "Stopped", icon="CHECKMARK" if running else "PAUSE")
        row = layout.row(align=True)
        row.operator("junkun_bridge.start")
        row.operator("junkun_bridge.stop")


CLASSES = (JUNKUNBRIDGE_Preferences, JUNKUNBRIDGE_OT_Start, JUNKUNBRIDGE_OT_Stop, JUNKUNBRIDGE_PT_Panel)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    poll = bpy.app.driver_namespace.pop("_junkun_blender_clay_bridge", None)
    if poll and bpy.app.timers.is_registered(poll):
        bpy.app.timers.unregister(poll)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

