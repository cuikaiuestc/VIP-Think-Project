# Jimeng Human Handoff

Use this reference when writing instructions for a human to operate Jimeng/Seedance or similar video tools.

## Current Boundary

Until a CLI/API is explicitly connected, treat video generation as manual:

- Codex prepares assets, prompts, settings, and checks.
- The user uploads files, selects model/options, spends credits, and downloads the original generated video.
- The user returns the original video to Codex for review.
- Codex does not claim that it generated or inspected a Jimeng result unless the user provided the output.

## Upload And Reference Contract

Give the user an exact reference map:

```text
@视频1 = previous segment original video, used for continuity
@图片1 = current segment opening keyframe
@图片2 = current segment process keyframe
@图片3 = current segment landing keyframe
```

For the first segment, there may be no `@视频1`; use character/style reference images instead.

When a previous segment exists, state that `@视频1` is responsible for continuity and the storyboard images are responsible for current segment control.

## Settings Contract

Specify:

- model, such as Seedance 2.0 Fast VIP when the user names it
- aspect ratio, such as 9:16 or 16:9
- duration, such as 10s or 15s
- reference mode, such as all-reference, first-last frame, smart multi-frame, or automatic match
- frame timing when the UI exposes transition durations

If UI details are uncertain or user screenshots show configurable fields, explain the intended distribution rather than pretending exact UI names are fixed.

## Prompt Structure

Use this order:

1. Continuity anchor: "基于 @视频1 继续扩展，不是重新开场。"
2. Identity lock: same person, face, body, costume, voice, and behavior.
3. Segment summary: duration and story action.
4. Time-coded beats.
5. Speech instruction, if any.
6. Overall style.
7. Negative constraints.
8. Failure checklist.

For time-coded beats, use exact ranges:

```text
00:00-00:03 ...
00:03-00:06 ...
00:06-00:10 ...
```

## Speech And Dialogue

When testing or requiring character speech:

- put the speech moment near a reference image that shows the face or side face
- allocate enough seconds for the line
- state that the character must visibly open the mouth
- distinguish on-screen speech from narration
- include the exact line in quotes

If the line is too long for the requested duration, warn the user and recommend shortening or extending the segment.

## Returned Video Requirements

Ask the user to return:

- the original generated video file, not only a compressed social platform repost
- the prompt/settings used, if changed manually
- any failed versions if the user wants diagnosis

If the original video cannot be returned, ask for:

- first frame, middle action frame, speech frame if any, and final frame
- a short description of any visible drift

Do not design the next segment from memory alone when continuity is important.
