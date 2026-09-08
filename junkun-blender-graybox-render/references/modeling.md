# Programmatic Blockout Modeling

## Build For Silhouette And Staging

- Start with bounding volumes that establish footprint, height, clearance, and subject scale.
- Add only details that change silhouette, articulation, contact, or shot readability.
- Use repeated modules for wheels, windows, columns, steps, barriers, and debris.
- Keep bevel width proportional to object size; small bevels improve Workbench readability without pretending to be final topology.
- Use restrained material groups to separate semantic regions: subject, environment, moving parts, hazards, and effects.

## Editable Structure

- Create one scene per substantial previs version when the existing scene must remain intact.
- Use numbered collections such as `01_ENVIRONMENT`, `02_SUBJECTS`, `03_MOTION_RIGS`, `04_FX`, and `05_CAMERAS`.
- Parent multipart subjects to a root empty. Add nested pivots for turret, door, wheel, weapon, or other articulated motion.
- Keep mesh origins meaningful. Apply scale, but preserve rotations when they define local articulation axes.
- Store intent in custom properties or scene notes: units, forward direction, action axis, assumed heights, and placeholders.

## Environments

- Protect a clear action corridor before adding set dressing.
- Model foreground, action plane, and background as separate depth layers.
- Place obstacles based on blocking and camera parallax.
- For ruins, break masses into walls, floors, apertures, and rubble clusters instead of one undifferentiated cube.
- Avoid high object counts that add no visible information at preview resolution.

## Animation-Friendly Modeling

- Animate parent empties for vehicles and assemblies.
- Use separate pivots for recoil, steering, doors, turrets, and props.
- Do not keyframe duplicate child parts when one rig transform can carry them.
- Use explicit story-beat markers before secondary motion.

