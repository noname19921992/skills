# MiniMax H3 Adapter

## Purpose

Compile the performance master into an executable MiniMax H3 prompt. H3's prompt wrapper differs from Seedance: choose the mode first, then write the fields required by that mode.

## Current Constraint Snapshot

- Finished videos are 4–15 seconds at 24 FPS with native stereo audio.
- Common aspect ratios include 21:9, 16:9, 4:3, 1:1, 3:4, and 9:16; first-/last-frame modes generally follow the input image ratio.
- Prompts may contain no more than 7,000 characters.
- The simple first-/last-frame entry accepts 0–2 images.
- The full-reference entry accepts up to 9 images, 3 videos, and 3 audio files, with no more than 12 files total; video and audio also have per-clip and total-duration limits.

These limits are a current workflow snapshot. If the user is ready to submit and the current H3 interface shows different limits, follow the interface.

## Choose a Mode

- No assets: T2VA.
- One image defines the opening: I2VA.
- Two images define the opening and ending: FL2VA, using a continuous shot for the transition by default.
- One image defines only the ending: L2VA.
- Mixed images, video, and audio, or a request involving editing, continuation, or separated asset responsibilities: full-reference mode.

Give each input asset one clear responsibility: identity/appearance, scene, product, style, action, rhythm, camera, source-video edit, sound, or music. Do not treat every asset as generalized inspiration.

## Format Rules Shared by All Output Languages

English is the default output language. If the user explicitly requests another language, that choice changes only the body text inside fixed fields, not H3's format. The following must remain exactly as written even in a non-English prompt:

- English field names and their order;
- `<Picture N>`, `<Subject N>`, `<Video N>`, and `<Audio N>`;
- `[Shot N]` and the `MM:SS.mmm` time format for later shots;
- `(S1)`, `(S2)`, and `<d>[Language] ...</d>`;
- English frame-alignment sentences for I2VA, FL2VA, and L2VA;
- English task types and retention markers for Ref2VA.

Do not replace this wrapper with custom translated headings such as sections for references, core setup, visual process, or exclusions. Integrate exclusions naturally into the main description; do not add a separate negative-prompt field that H3 does not support.

## T2VA / I2VA / FL2VA / L2VA Output

In every output language, use these fields in this exact order:

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

For I2VA, add this sentence at the beginning:

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
```

For FL2VA, add this sentence at the beginning and replace `N` and `S.SS` with the actual final shot and total duration:

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
```

For L2VA, add this sentence at the beginning:

```text
How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

Leave one blank line after the alignment sentence. T2VA has no alignment sentence.

For a user-requested non-English output, write that language after the colons in `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music`. Do not translate the field names or change their order. Put a single prompt in one `text` code block. Inside the code block, do not add a title such as "Final Prompt," explanations, JSON, tables, or extra fields.

Example structure for a non-English T2VA prompt:

```text
integrated_multimodal_description: [Shot 1] [Body text in the requested language describing the cinematic style, characters, environment, and initial action]...

overall_soundscape: [Body text in the requested language describing room tone, natural breathing, and clothing friction]...

non_diegetic_music: N/A
```

I2VA, FL2VA, and L2VA prompts in another language still begin with the corresponding English alignment sentence, followed by a blank line and the three fixed fields.

## Full-Reference Mode

Regardless of body language, use this exact order:

```text
subject_definitions:
...

summary:
...

retention_analysis:
...

detailed_description:
[Shot 1] ...

overall_soundscape:
...

non_diegetic_music:
...
```

Label meanings:

- `<Subject N>`: A person, object, environment, costume, style, or action subject that must be tracked across shots.
- `<Picture N>`: A specific first frame, keyframe, last frame, composition, or storyboard anchor.
- `<Video N>`: Source video being edited or continued, or a timing, camera, or motion reference.
- `<Audio N>`: Independent audio to copy or reference, or audio from a source video.

Keep each label's meaning stable throughout. In a non-English output, explanations may use the requested language after the colon and fixed markers, but the six field names, bracketed task types, and markers must remain in English. For visible content, `retention_analysis` may use only `fully_preserved`, `partially_preserved`, `attribute_transfer`, and `weak_reference`; for audio, use only `fully_copy`, `partially_copy`, `reference`, and `weak_reference`.

## Shots and Time

- Write `[Shot 1]` for the first shot, with no start time.
- Write later shots as `[Shot N] At MM:SS.mmm, the camera cuts to...`, with strictly increasing times.
- Cut only when viewpoint, state, space, or time changes materially.
- Express authentic human presence within a single shot through continuous action phases, not time headings disguised as cuts.
- FL2VA uses one continuous shot by default to move credibly from first frame to last frame. Do not add intermediate cuts unless the user explicitly requests them.
- State the camera movement type clearly; add amplitude and speed only when they matter.

## Compression Strategy for Human Presence

H3 is limited to 15 seconds. Do not squeeze a 30-second Seedance performance into that duration by shortening every line. Compress in this order:

1. Preserve the character objective, trigger, and ending relationship change.
2. Preserve one protective behavior as the performance baseline.
3. Preserve one comprehension delay, the most important involuntary leak, and one choice.
4. Preserve containment or aftermath after the outburst.
5. Remove repeated micro-actions, a second emotional escalation, decorative camera movement, and environmental details that do not affect causality.

A 15-second relationship scene generally supports one complete turn. Split multi-stage revelations into multiple generations rather than sacrificing listening and reaction time.

## Dialogue and Sound

- Assign a stable `(S1)`, `(S2)`, and so on to every speaking character.
- Put only words that are actually spoken inside `<d>[Language] exact original words</d>`; never alter them without permission.
- For off-screen speech, write `says in an off-screen voiceover` and state that visible characters keep their lips closed.
- Put ambience, action sounds, and nonverbal vocalization in `overall_soundscape`.
- Put music heard by the audience but not the characters in `non_diegetic_music`; write `N/A` when there is none.
- Dialogue, live music, and playback within the scene are diegetic sounds; do not duplicate them in non-diegetic music.

## Check

- Mode, duration, aspect ratio, and asset count are compatible.
- First-/last-frame labels align with the actual shot and time.
- Character identity, costume, props, voice IDs, and asset responsibilities are not crossed.
- Dialogue fits within the shot while leaving time for listening, comprehension, and aftermath.
- The three- or six-field order is correct, and sound layers are not misplaced.
- A non-English prompt translates only field-body text and does not translate or replace field names, labels, alignment sentences, task types, retention markers, or shot formatting.
- A single final prompt contains only one `text` code block, with no explanation, table, custom translated section, or separate negative-prompt field inside it.
- The final prompt does not exceed 7,000 characters.
