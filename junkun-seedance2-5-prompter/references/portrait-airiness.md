# Portrait Airiness

## Scope

This module translates a premium, airy portrait look into executable lighting, color, spatial, and lens rules. It addresses only the visual cinematography layer; it does not replace the character objectives, stimulus–reaction chain, self-repair, or emotional residue in [human-presence-method.md](human-presence-method.md).

The design is informed by VoxCat's article ["The 'Airiness' of AI Photography Comes from Breathing, Not Pixels"](https://x.com/VoxcatAI/status/2030845228891127830). The static-photography ideas are reorganized here as rules for video generation.

## Activation Conditions

Enable this module when the user explicitly asks for directions such as:

- Premium portraiture, airiness, luminous clarity, softness, or translucence;
- Fashion editorial, beauty photography, or magazine portraiture;
- Ethereal or dreamlike portraiture, light soft focus, or Soft Bloom;
- A provided reference image clearly depends on soft backlight, a clean palette, and restrained highlight diffusion, and the user asks to preserve that photographic language.

Do not enable it merely because a person appears in the frame. Keep it off by default for documentary, news, hard light, film noir, horror, war, crime, gritty realism, strong stage lighting, requests for real location light, or any reference lighting already locked by the user that conflicts with this module.

## Core Structure

### 1. Use Backlight as the Spatial Skeleton

Place a motivated rim source behind or behind-and-to-the-side of the subject, such as a window, sky, doorway, softbox, or practical light. Its purpose is to separate hair, shoulders, and facial contour slightly from the background, not to draw an even glowing outline around the entire person.

Specify:

- Direction and height of the source;
- Which contours receive light;
- Strength and width of the bright edge;
- How it naturally weakens, becomes occluded, or shifts as the character moves or turns.

Avoid sourceless halos, equal-width full-body outlines, blown-out hair, and backlight passing through solid objects.

### 2. Preserve the Face with a Large Soft Source

Use a broad soft source in front of or slightly to the front side of the subject to balance the backlight and keep the eyes, sides of the nose, jaw, and skin tone readable. Soft light may ease harsh shadows but must not erase facial volume.

Preserve:

- Natural skin tone and age characteristics;
- Facial bone structure and subtle tonal transitions;
- Real skin texture without emphasizing every pore;
- Necessary definition in the eyes, lashes, brows, and lip edges.

Avoid flat shadowless faces, porcelain-doll skin, uniform brightness across the face, excessive skin smoothing, and additional beauty reshaping.

### 3. Restrain the Palette and Define Color-Temperature Relationships

Limit background elements and the number of competing colors. Prefer one dominant color family with a small number of supporting hues. Keep the background clean and quiet so the person remains the visual focus.

A cool blue-gray background with relatively warm skin is an option, not a fixed template. Color temperature must respect the user's requested style, scene sources, natural skin tone, and reference assets. Do not desaturate everything automatically to make it look "premium," and do not let red, yellow, and green background elements compete simultaneously.

### 4. Apply Soft Bloom Only to the Brightest Highlights

Allow the brightest hair edges, nose highlights, jewelry reflections, petal edges, window light, or practical lights to diffuse slightly outward. Bloom must preserve the highlight core and object boundary, creating optical lens diffusion rather than overall blur.

Maintain:

- Low intensity, local application, and gradual falloff;
- Clear eyes and primary facial structure;
- Tonal depth in midtones and shadows;
- Continuous bloom radius and strength across adjacent shots.

Avoid global white haze, lifted blacks, universally soft edges, exposure flicker, bloom that changes size abruptly, and depth-of-field blur mislabeled as bloom.

### 5. Use Spatial Layering Instead of Quality-Word Piles

Do not rely on stacks of terms such as `8K`, `ultra detailed`, `sharp focus`, or `masterpiece` to create a premium image. Prefer describing:

- Distances among foreground, subject, and background;
- How light falls off through air, translucent materials, hair, and edges;
- Which parts of the subject remain crisp and which are softened;
- How simplified the background is and how much color weight it carries;
- How focus and exposure remain stable through camera movement.

## Video Continuity

Once static portrait rules enter video, they must follow physical continuity:

- Rim light and facial fill change with distance as the character approaches or moves away from the source.
- When the character turns, the bright edge appears only on contours still facing the source.
- Bloom, focus, and background blur change smoothly after camera movement, without sudden jumps.
- Hair, sheer fabric, and airborne particles move only in response to wind, bodily action, or environmental disturbance.
- Maintain source direction, background color family, skin tone, and exposure logic across shots unless the story includes an explicit lighting change.
- Bloom and shallow depth of field must not obscure gaze, hand action, or prop state during a key micro-reaction.

## Combine with Authentic Performance

Lighting serves what the character is doing; it does not announce the emotion for them:

- Use backlight to separate the character from the space, not a halo to symbolize "ethereal" or "sad."
- Use soft light to preserve listening reactions, not shadowless beautification that hides the jaw, breathing, or changes in gaze.
- Keep protective behavior, unfinished action, and emotional residue as priorities.
- When performance information competes with decorative light, reduce bloom, background brightness, or color complexity.

## Write It for the Target Model

### Seedance 2.5

Put this module into the global lighting, palette, texture, and cinematography rules. Describe corresponding changes on the timeline only when the source, space, or character position changes; do not repeat the entire lighting specification mechanically in every time range.

### MiniMax H3

Do not add custom fields:

- T2VA, I2VA, FL2VA, and L2VA: Write it inside `integrated_multimodal_description`.
- Ref2VA: Write it inside `detailed_description`. If lighting or palette comes from reference assets, preserve the corresponding labels and relationships in `subject_definitions` and `retention_analysis`.
- Do not put visual lighting effects in `overall_soundscape` or `non_diegetic_music`.

A non-English H3 prompt still preserves fixed English field names, alignment sentences, labels, and shot-time formatting.

## Control Density

For ordinary requests, one compact instruction is enough:

> Motivated soft side-backlight lightly traces the hair and shoulders, while a broad frontal-side soft source preserves natural skin tone and facial volume. Keep the background palette clean and restrained. Only the brightest hair edges and jewelry reflections receive subtle local Soft Bloom; the eyes and primary facial structure stay crisp, with no global haze or plastic skin smoothing.

Expand source placement, character movement, palette, focus, and bloom changes only for high-control portraiture, complex movement, cross-shot lighting continuity, or a user-requested cinematography plan.

## Check

- The user actually requested airiness or a related portrait direction; the module was not activated merely because a person appears.
- Backlight and soft light have explainable directions and spatial sources.
- Rim light does not form a sourceless halo attached to the person.
- Soft light preserves facial volume, age, natural skin tone, and skin structure.
- The palette is restrained without mechanically imposing cool blue-gray or unjustified desaturation.
- Soft Bloom affects only the brightest regions, leaving the subject and action readable.
- Lighting, exposure, focus, and bloom remain continuous through character and camera movement.
- Portrait airiness does not override plot, performance causality, identity, or reference-asset constraints.
- The final text uses concrete cinematography instructions rather than a pile of resolution and quality terms.
