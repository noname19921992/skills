# Cinematic Camera Design

## Begin With Dramatic Function

Every shot needs one primary job: establish geography, reveal information, track action, emphasize impact, show reaction, or transition. Do not add movement merely because the camera can move.

For each shot define:

- subject and story beat;
- opening and landing composition;
- shot size and camera height;
- lens and working distance;
- camera path and look target path;
- duration and speed profile;
- continuity relationship to adjacent shots.

## Spatial Continuity

- Establish the action axis from subject travel, eyelines, or opposing forces.
- Keep cameras on one side for readable screen direction unless crossing is motivated.
- Cross via a neutral/on-axis shot, a visible camera move across the axis, or a new establishing shot.
- Preserve look room and travel room. Landing frames should anticipate the next action or cut.

## Lens As Staging

- Wide lenses emphasize geography, speed, foreground parallax, and spatial distortion.
- Normal lenses balance subject and environment.
- Longer lenses isolate, compress depth, and make lateral movement read strongly.
- Change lens only for a storytelling reason. Prefer moving the camera when perspective must change.
- Check clipping and near-foreground distortion in wide moving shots.

## Robust Blender Camera Rig

- Animate a camera object and a separate target empty.
- Use `TRACK_TO` with negative Z tracking and Y up, or a stable damped-track setup.
- Animate both camera and target when attention shifts.
- Use parent empties for crane, dolly, orbit, or handheld layers when independent controls help.
- Use timeline camera markers for multi-shot sequences.
- Keep active scene camera and marker assignments explicit.

## Motion Design

- Design opening, change, and landing, not merely two positions.
- Prefer arcs or layered movement when revealing depth; use straight paths when clarity and force matter.
- Accelerate into purposeful motion and settle before a cut unless impact requires abruptness.
- For tracking shots, vary target height subtly with subject posture instead of locking mechanically to the origin.
- Add shake only as a small secondary layer after the primary path works.
- Tie impacts to a short camera response, then recover; do not let noise obscure framing.

## Blocking Versus Polish

- Blocking: linear interpolation, clear positions, simple targets, low-cost render.
- Polish: Bezier easing, custom handles, path refinement, subtle lens/focus changes, secondary motion.
- Review frame-to-frame angular speed. Smooth location does not guarantee smooth rotation when the target crosses near the camera.

## Shot Manifest

Store at least:

```json
{
  "name": "S01_Establish",
  "start": 1,
  "end": 120,
  "purpose": "establish geography and travel direction",
  "lens_mm": 28,
  "camera_move": "descending lateral push",
  "subject": "main vehicle"
}
```

