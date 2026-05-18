# Workflow Reference

Use this reference when running the complete AI video production loop or when the user asks what comes next.

## Stage Map

1. Requirement brief
   - Input: explicit user demand for a video.
   - Output: production brief with goal, audience, duration, platform, aspect ratio, story premise, and constraints.
   - Gate: confirm the brief if it changes story scope, style, or required tools.

2. Script structure
   - Output: story outline, segment map, character bible, world bible, dialogue rules, and continuity risks.
   - Keep the script operational. It must guide images and video prompts, not read like literary prose.

3. Current segment selection
   - Output: one current segment only, with start state, end state, objective, and 2-4 beats.
   - Segment length is normally 10-15 seconds. Use the user's model limit or budget when specified.

4. Storyboard image generation
   - Output: 2-4 keyframe prompts or generated images for the current segment.
   - The usual structure is opening frame, process frame, landing frame.
   - Add a fourth frame only when the segment has a major action turn or speech moment that needs extra control.

5. Human Jimeng/Seedance handoff
   - Output: copy-ready prompt, upload order, reference mapping, model settings, duration, aspect ratio, and negative constraints.
   - Stop for the human to generate the video unless the user explicitly asks to continue only with text planning.

6. Returned video review
   - Input: original generated video, not just a subjective summary.
   - Output: pass/retry decision, actual ending state, drift list, and next-segment carry-over constraints.

7. Next segment iteration
   - Use the actual ending frame and motion from the returned video.
   - Design the next segment's storyboard and prompt only after review.

## Artifact Order

Recommended artifact names when writing files:

- `production_brief.md`
- `script_structured.md`
- `continuity_bible.md`
- `segment_01_storyboard.md`
- `segment_01_image_prompts.md`
- `segment_01_video_prompt.md`
- `segment_01_review.md`
- `segment_02_storyboard.md`

Do not require file creation for every run. Use files when the project is long, collaborative, or likely to be resumed later.

## Segment Decision Rules

- Use 10 seconds when credits, model limits, or speech testing require lower cost.
- Use 15 seconds when the segment includes enough physical action to need breathing room.
- Split the segment when it contains more than one location change, one important speech beat, or one continuity-sensitive prop transition.
- Keep speech moments near a controlled storyboard frame. If the face must speak, include a frame that supports a visible face angle.

## Stop Conditions

Stop and ask for user action when:

- the next step requires paid video generation in Jimeng/Seedance
- the previous segment video has not been returned
- the user asks to make a continuity-sensitive next segment but only provides the original plan
- a character, face, voice, or direction mismatch would make later continuity unreliable

## Failure Handling

Use the smallest recovery path:

- Missing previous video: request the original video or representative frames. Do not finalize the next segment.
- Weak continuity but usable ending: enter the next segment with explicit repair constraints.
- Direction, identity, or costume mismatch: recommend rerun unless the user accepts a visible discontinuity.
- Speech required but mouth not visible: mark as failed for dialogue validation even if the visual frame looks good.
- Tool UI differs from expected settings: describe the intended reference behavior instead of forcing stale UI labels.
- User wants to save credits: compress duration or use first-last frame tests, but keep the same continuity checks.
