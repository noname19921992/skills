# Seedance 2.5 Adapter

## Purpose

Compile the platform-neutral performance master into a copy-ready Seedance 2.5 directing prompt. These rules draw on the user's existing Seedance workflow and the open-source [seedance-2-5-video-director](https://github.com/liyue-aigc/seedance-2-5-video-director), with the scope narrowed to natural human performance and relationship scenes.

## Modes and Capabilities

Choose the mode according to the user's current interface. The following is a capability snapshot dated 2026-08-16 and should be used only when the plan materially depends on a limit:

- Standard generation, first-frame, first-and-last-frame, and comprehensive-reference modes: roughly 4–30 seconds.
- Long Video: roughly 30–180 seconds.
- Supports image, video, and audio references, as well as continuation, video editing, transitions, and multi-panel storyboard workflows.

Platform entries and limits may change. When the interface conflicts with this snapshot, follow the current interface and tell the user what differs.

## Reference-Asset Responsibilities

Normalize the user's existing assets in order of appearance as `@Image N`, `@Video N`, and `@Audio N`. For each asset, specify:

`label | used for | preserve | do not inherit | active scope`

Example:

> @Image 1 defines the daughter's identity, apparent age, face, body type, and all visible clothing; do not inherit the source background, pose, crop, or lighting.  
> @Video 1 references only the mother's rhythm of repeatedly folding clothes and the delay in her hand movement; do not inherit actor identity, clothing, scene, camera position, or sound.

An ordinary "character reference image" constrains the complete visible person by default, including identity, hairstyle, body type, clothing, shoes, and accessories. Narrow the responsibility only when the user explicitly says "face only" or permits a wardrobe change.

## Recommended Assembly Order

Simple scenes may use continuous natural language. For high-control scenes, use this order:

1. Output declaration: duration, aspect ratio, degree of realism, single or multiple shots, and dialogue language.
2. Asset mapping: responsibility and exclusion scope for each reference.
3. One-sentence intent: characters, place, event, relational pressure, and ending direction.
4. Global setup: characters, protective behavior, space, props, camera, lighting, and sound baseline.
5. Continuous timeline: trigger, visible reaction, choice, camera, and ending state for each range.
6. Human-presence rules: only shared rules not already expressed adequately on the timeline.
7. Sound: exact dialogue, speaker, ambience, body sounds, music, and subtitles.
8. Continuity and exclusions: identity, wardrobe, axis, prop state, lip movement, emotional residue, and high-risk unwanted errors.

## Timeline

- Use continuous, non-overlapping time ranges that cover the full duration, such as `0–4s, 4–9s, 9–15s`.
- Give each range only one main relational or state change.
- State the bodily, object, and relational conditions at the end of the range; the next range starts from them.
- The character must receive the stimulus before reacting. Actions triggered by a dialogue keyword occur after that word.
- When there are too many actions, reduce the number of events rather than hiding overload with denser timestamps.
- Time ranges in a single shot are performance beats, not cuts. Do not combine "single shot" with hard cuts, viewpoint jumps, or impossible camera changes.

## Performance Language

Seedance final prompts should prioritize visible action and audible sound:

- Write `She prepares to inhale but completes only half of it; her right hand stops folding the cuff half a beat late.`
- Avoid relying on `She is conflicted, shocked, sad, and performs cinematically.`
- Use only a few high-value signals per beat; avoid animating facial anatomy one component at a time.
- State exactly how the character is trying to maintain normality.
- Specify self-awareness and containment after an outburst so the character does not escalate continuously until the end.

## Dialogue and Sound

- Preserve dialogue verbatim. Specify the character, on-screen/off-screen status, language, and change in tone.
- Visible characters move their lips only when speaking their own lines. While listening to off-screen dialogue, keep their mouths closed and respond physically.
- Leave time for listening, comprehension, breathing, and the aftermath of a line.
- Prioritize ambience over music. Specify the exact position of key object sounds and silence.
- In exclusions, state whether there is no extra voiceover, no wrong speaker, no altered dialogue, and whether subtitles are absent or present.

## Dual-Model Consistency Card

If the same concept also needs an H3 version, lock these before compiling:

- Character identities and relationships;
- Exact dialogue and speakers;
- Every trigger signal and primary reaction;
- Protective behavior and key prop state chain;
- Opening and ending states;
- Shot form, sound priorities, and exclusions.

When Seedance supports a longer timeline, do not invent new events that change the story's meaning. If a shorter H3 version is required, preserve the trigger, one leak, one choice, and ending residue first.
