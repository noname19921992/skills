# Authentic Human-Presence Diagnosis

When diagnosing an existing prompt, identify the main issues that directly affect generation. Do not frame stylistic preferences as errors unless the user asks for that evaluation.

## Diagnostic Dimensions

### 1. Invisible Psychological Labels

Problem signal: The prompt says only sad, angry, shocked, conflicted, restrained, or cinematic performance.

Repair direction: Add a character objective, protective behavior, concrete trigger, visible leakage, and ending state.

### 2. Reaction Precedes the Stimulus

Problem signal: Before the key words are spoken, the character is already crying, stopping an action, or changing a decision.

Repair direction: Specify when the character hears or sees the trigger, leave a comprehension delay, and place the reaction after it.

### 3. Micro-Action Overload

Problem signal: The same second contains instructions for eyebrows, eyelids, nostrils, mouth corners, swallowing, fingers, shoulders, and breathing.

Repair direction: Select one primary action and 1–3 signals per beat, prioritizing details that change the action or relationship.

### 4. Random Realism Noise

Problem signal: Unmotivated blinking, looking around, constant handheld shake, deliberate defocus, or random small movements.

Repair direction: Tie every imperfection to attention, pressure, or self-repair; remove noise without causal purpose.

### 5. No Protective Layer

Problem signal: The character jumps directly from neutral to a standardized emotional expression, as if waiting for a director's cue.

Repair direction: Give the character a continuing task or behavioral strategy so pauses, repetitions, speed changes, and failures have a visible baseline.

### 6. No Emotional Residue

Problem signal: After a cut, posture, breathing, gaze, objects, and emotion reset to defaults.

Repair direction: Define an ending state for each beat and carry it into the next; build character and prop state chains.

### 7. Only the Speaker Performs

Problem signal: The listener is completely still, fakes lip movement, or mirrors the speaker's expressions in sync.

Repair direction: Give the listener independent perception, comprehension, and response timing. When listening to off-screen dialogue, explicitly keep the lips closed.

### 8. Dialogue Overload

Problem signal: The text only just fits when read quickly, leaving no time to prepare to speak, pause, act, or absorb the aftermath.

Repair direction: Cut lines, split the shot, or extend the duration; do not solve the problem by speeding up all dialogue.

### 9. Camera and Performance Compete

Problem signal: A key micro-reaction coincides with a fast orbit, whip pan, sudden close-up, strong depth-of-field shift, or many transitions.

Repair direction: Keep the camera readable during the key comprehension beat; trigger cuts through relationship or information changes.

### 10. Sound Performs Instead of the Character

Problem signal: Sentimental strings, heartbeat, low-frequency impact, or crying begins before the emotion; silence is filled completely.

Repair direction: Rely first on dialogue, breathing, contact sounds, and ambience. Bring music in later, keep it beneath the performance, or omit it.

### 11. Platform Syntax Is Mixed

Problem signal: Seedance asset labels and H3 fields appear in one final prompt; H3 mode, alignment sentences, or sound fields are incorrect.

Repair direction: Recover the shared performance master, then compile two independent versions.

## Diagnostic Output

For diagnosis-only requests, use:

1. `Conclusion`: State in one sentence the issue that most weakens authentic human presence.
2. `High-Priority Issues`: Cite the specific source line or time range, explain why it will fail, and give the repair direction.
3. `Keep`: Identify effective decisions in the existing prompt that should be preserved.
4. `Platform Issues`: Add only when there is a real conflict in mode, labels, duration, or fields.

If the user requests a revision, provide the complete revised prompt afterward. In diagnosis-only mode, do not silently replace the original.
