---
name: junkun-seedance2-5-prompter
description: Rewrite video ideas, scripts, existing prompts, or reference assets into Seedance 2.5 and MiniMax H3 prompts with authentic human presence. Use for natural live-action performance, dialogue scenes, emotional turns, micro-reactions, reducing AI-like behavior, character interaction, airy portrait cinematography, performance diagnosis, and dual-model adaptation of the same concept; not for scenery-only videos, product turntables, or videos without character performance.
---

# junkun seedance2.5 prompter

Translate psychological states into behavior that a camera can see, a microphone can hear, and a performer can complete within the available time. The core deliverable is a platform-neutral performance master, compiled separately for each target model. Never copy one model's labels or constraints directly into another.

## Establish the Task

Lock the following information from the user's request. Do not alter anything already provided:

- Target platform: `Seedance 2.5`, `MiniMax H3`, or `both models`.
- Task type: generation from scratch, first-/last-frame control, multimodal reference, continuation, editing, diagnosis, or prompt optimization.
- Duration, aspect ratio, shot form, exact dialogue, subtitle policy, and music policy.
- The responsibility of each asset, including attributes that must be preserved and must not be inherited.
- Requested deliverable: prompt only, full directing plan, dual-model versions, diagnosis, or revision in the original structure.

Ask one brief question only when different answers would materially change the prompt. For other missing details, use restrained defaults and label them explicitly as added assumptions. If the user does not specify an output language, default to English.

## Build the Performance Master

Before writing the prompt, complete these cards internally. Keep them brief for simple scenes; do not expose the full reasoning unless it is useful to the user.

1. **Character objective**: What does the character want the other person to do, or what state do they want the scene to maintain?
2. **Protective behavior**: What ordinary task, posture, tone, or distance helps the character appear normal?
3. **Trigger signal**: Which exact line, sound, object, or action changes the character's state?
4. **Hidden contradiction**: What is the character trying to express, and what are they trying to suppress?
5. **Reaction chain**: Perception → brief comprehension → involuntary leak → deliberate response → self-repair → emotional residue.
6. **Relational feedback**: How does one person's behavior change the other's rhythm, distance, or strategy?
7. **State carrier**: How do a held object, ongoing action, breathing, spatial distance, or ambient sound maintain continuity across shots?
8. **Ending change**: How do the final relationship, bodily state, object position, or unfinished action differ from the opening?

For detailed rules, read [references/human-presence-method.md](references/human-presence-method.md).

## Control Density

Choose a density based on scene complexity rather than forcing every request into a full timeline:

- **Lightweight**: One character, one main action, roughly 4–8 seconds. Define the trigger, one primary action, one or two leakage signals, and the ending state.
- **Beat-based**: Roughly 8–15 seconds or one clear turn. Describe the reaction chain in continuous time ranges, with one main change per beat.
- **High-control**: Multi-character dialogue, more than 15 seconds, complex relationships, or precise performance. Use global performance rules, a continuous timeline, speaker/listener roles, prop state, sound, and continuity locks.

For each key beat, prefer `one primary action + 1–3 visible or audible signals`. When detail is overloaded, remove decorative camera language and repeated adjectives first, then secondary micro-actions. Preserve dialogue ownership, causality, identity, space, props, and the ending change.

## Add Portrait Airiness When Needed

When the user explicitly asks for `premium portraiture`, `airiness`, `luminous clarity`, `softness`, `fashion editorial`, `beauty photography`, `ethereal`, `dreamlike portraiture`, or `soft-focus bloom`, read [references/portrait-airiness.md](references/portrait-airiness.md). Apply it as a visual cinematography layer over the performance master. Do not confuse optical airiness with authentic human presence, and do not apply it automatically to documentary, hard-light, horror, war, crime, gritty realism, or scenes whose lighting style is already locked by the user.

Portrait airiness may change only lighting, palette, spatial layering, skin rendering, and highlight diffusion. It must not change character identity, age, natural skin tone, plot, performance rhythm, prop state, or the locked scope of reference assets.

## Compile for the Target Model

### Seedance 2.5

Before generating, read [references/seedance-2-5-adapter.md](references/seedance-2-5-adapter.md). Bind reference responsibilities explicitly with `@Image N`, `@Video N`, and `@Audio N`. Organize the output around global intent, asset responsibilities, space and characters, temporal progression, sound, continuity, and exclusions. Keep ordinary requests naturally readable; use layered headings only for complex performances.

### MiniMax H3

Before generating, read [references/minimax-h3-adapter.md](references/minimax-h3-adapter.md). First choose T2VA, I2VA, FL2VA, L2VA, or full-reference mode, then use the corresponding fields, shot labels, dialogue tags, and sound layers. Regardless of whether the body is in English or another user-requested language, H3's fixed field names, field order, English alignment sentences, reference labels, and shot-time format must remain exact. A non-English output must not replace them with custom translated headings.

### Both Models

Build a single performance master, then generate independently:

1. `Seedance 2.5 Final Prompt`
2. `MiniMax H3 Final Prompt`

Both versions must preserve the same story facts, performance turn, dialogue, character states, and ending. Beat density may differ because of platform duration or formatting constraints; explain the tradeoff in one sentence before the prompts. Do not put Seedance `@Image` syntax into H3, and do not copy H3's six-field wrapper into Seedance.

## Output Modes

Follow the user's requested delivery format:

- **Prompt only**: Output only the copy-ready final code block, with no instructional explanation.
- **Full directing plan**: Output added assumptions, a performance-master summary, asset mapping, continuity, and the final prompt.
- **Dual-model versions**: Briefly summarize the shared performance master, then provide two independent final prompts.
- **Diagnosis only**: Use [references/diagnosis.md](references/diagnosis.md) to identify problems without silently rewriting the prompt.
- **Optimize/rewrite**: Preserve the original story, dialogue, asset responsibilities, and user-specified structure. Fix only executability and authentic human presence, then briefly summarize material changes.

Default all explanations and prompt prose to English. Preserve dialogue, lyrics, on-screen text, and proper nouns in their original language unless the user explicitly asks for translation. If the user explicitly requests another output language, use it for explanations and prompt prose while retaining any platform-required English syntax.

## Final Check

Before delivery, confirm:

- Reactions occur after the character perceives the stimulus, with a comprehension delay appropriate to the context.
- The character has a concrete objective and protective strategy; micro-actions arise from pressure rather than random motion.
- Both speakers and listeners perform; a silent character does not fake lip movement.
- Emotion leaves residue in the next beat; characters and props do not reset across cuts.
- A single beat does not overload blinking, swallowing, fingers, mouth corners, shoulders, and breathing instructions.
- Expressions may contain slight asymmetry, offsets, and incompletion, but no deliberately manufactured errors or meaningless motion.
- The camera can read each key reaction; camera movement and cuts do not compete with character action.
- Dialogue, pauses, actions, and reactions can be completed naturally within the duration.
- Ambient sound, body sound, dialogue, and music have a coherent hierarchy; music does not cover key silence.
- When portrait airiness is enabled, backlight has a plausible source, frontal soft light preserves facial structure, highlight bloom is localized and restrained, skin tone and age are not smoothed away, and lighting remains continuous through character and camera motion.
- Platform mode, reference labels, duration, fields, timeline, and asset count are mutually compatible.
- An H3 prompt in a user-requested non-English language still uses the fixed three- or six-field wrapper, without custom translated sections or an independent negative-prompt field.

Platform limits may change. Verify the current interface only when the user is preparing an actual submission and a limit affects the plan. If verification is unavailable, identify the snapshot being used; do not invent new limits or promise success in a single generation.
