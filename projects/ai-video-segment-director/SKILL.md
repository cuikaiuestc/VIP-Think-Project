---
name: ai-video-segment-director
description: Plan and supervise segmented AI video production from a clear video requirement through script structure, character/style anchoring, current-segment storyboard images, Jimeng/Seedance prompt handoff, returned-video continuity review, and next-segment iteration. Use when the user wants to create an AI short film or video by segment, maintain character face/body/voice consistency, generate storyboard prompts, generate Jimeng prompts with @reference images/videos, or review each generated segment before designing the next one.
---

# AI Video Segment Director

Use this skill to turn a clear video requirement into a controlled segmented AI video workflow. The core job is to reduce generation drift by treating every segment as a loop: plan current segment, generate storyboard images, hand off to the human video tool, inspect the returned original video, then design the next segment from the real ending frame.

Default output language is Simplified Chinese. Keep stable tool names such as Jimeng, Seedance, GPT-Image, `@视频1`, `@图片1`, CLI, API, and Markdown in English or mixed form when useful.

## Operating Contract

- Start from the user's explicit video requirement, not from a copied article, case study, or personal example.
- Keep article/case references as optional inspiration only when the user provides them; do not make them required inputs.
- Treat Jimeng/Seedance as a human-operated tool until a CLI/API is explicitly available. Provide exact upload, reference, duration, aspect-ratio, and prompt instructions for the user to perform manually.
- Require the original generated video for every completed segment before designing the next segment. If the video cannot be inspected, pause or request still frames/screenshots instead of inventing continuity.
- Control consistency at every layer: script, character bible, storyboard image prompts, video prompts, negative prompts, and returned-video review.
- Do not pre-generate storyboard images for later segments unless the user explicitly overrides the iterative workflow.
- Separate creative decisions from tool operations. The skill directs story, continuity, and prompt contracts; the human runs paid video generation unless automation is later connected.

## Mode Selector

Choose the narrowest mode before producing artifacts:

| Mode | Use When | Output |
|---|---|---|
| `new-project` | The user provides a new video requirement. | Production brief, script structure, continuity bible, and first segment plan. |
| `current-segment` | The user is ready to generate the current segment. | Current segment storyboard prompts and Jimeng/Seedance handoff. |
| `prompt-only` | The user already has images/video references and asks only for a video prompt. | Copy-ready prompt, negative prompt, and settings notes. |
| `returned-video-review` | The user returns a generated segment. | Pass/rerun decision, actual ending state, drift report, and next-segment constraints. |
| `next-segment` | The previous segment has been reviewed and the user wants to continue. | Next segment plan, storyboard prompts, and video prompt based on the real ending. |

If the user asks for a later segment without returning the prior video, switch to `returned-video-review` requirements first. Provide only a clearly labeled provisional outline if useful.

## Non-Goals

- Do not replace the human's final creative taste call. This skill structures decisions and checks continuity.
- Do not claim direct Jimeng/Seedance execution, upload, credit spending, or download unless a real CLI/API integration is available in the environment.
- Do not treat generated storyboard images as final video quality proof. The returned video is the truth source for continuity.
- Do not optimize for one model provider only. Jimeng/Seedance is the current handoff target, but the workflow should remain portable to similar image-to-video tools.
- Do not hide weak continuity behind prettier wording. If a segment will cause later mismatch, recommend rerun or mark it as a test-only output.

## Reference Loading

Read only the reference needed for the current step:

- `references/workflow.md`: end-to-end staged workflow, required artifacts, and stage gates.
- `references/continuity-controls.md`: face, body, costume, voice, mouth, object, space, lighting, and style controls across layers.
- `references/jimeng-human-handoff.md`: human Jimeng/Seedance operation contract, `@` reference usage, and returned-video requirements.
- `references/segment-output-contract.md`: output templates for storyboard briefs, image prompts, video prompts, review reports, and next-step instructions.

## Workflow

### 1. Requirement Intake

Collect or infer:

- video goal, audience, platform, aspect ratio, total duration, and target segment length
- story premise, required scenes, required actions, required dialogue, and forbidden content
- character count, character identities, appearance, age, costume, voice, accent, and performance style
- visual style, camera language, pacing, realism level, and reference materials
- generation tools available, including image model, Jimeng/Seedance model, max duration, and whether `@` references are supported

If the requirement is too vague, ask only the smallest set of questions needed to define the first production slice.

Gate: confirm the production brief before treating the script direction as stable.

### 2. Script And Continuity Bible

Convert the requirement into:

- concise story outline
- segment map by time range
- character bible for face, body, age, costume, voice, accent, behavior, and emotional range
- world bible for location, season, lighting, weather, color, props, and camera style
- dialogue rules, especially whether speech must be visible on screen with lip movement
- continuity risks that must be checked after each segment

For detailed consistency controls, read `references/continuity-controls.md`.

Gate: confirm character and style anchors before generating storyboard images.

### 3. Segment Plan

Select only the current segment. Usually use 10-15 seconds unless the user's tool limit or budget requires another length.

For the current segment, define:

- segment objective
- start state inherited from the previous video or from the opening setup
- end state needed for the next segment
- 2-4 storyboard beats, usually opening, process, and landing image
- reference order such as `@视频1`, `@图片1`, `@图片2`, `@图片3`
- must-preserve continuity and must-avoid drift

If this is not the first segment, inspect the returned previous video before writing this plan.

### 4. Storyboard Image Prompts

Generate storyboard image prompts only for the current segment. Each prompt must specify:

- frame role and time beat
- subject identity and continuity anchors
- action and body position
- composition, camera distance, lens feel, and movement implication
- environment, lighting, weather, prop state, and direction of travel
- style constraints and negative constraints

The storyboard images act as video-control frames, not decorative concept art.

### 5. Human Video Handoff

Prepare a copy-ready Jimeng/Seedance handoff:

- what assets to upload and in what order
- which mode to choose, such as first-last frame, multi-frame, all-reference, or automatic match
- aspect ratio, duration, model, and any configurable transition timings
- exact prompt with `@视频` and `@图片` references embedded at the relevant time beats
- negative prompt and failure checklist

Read `references/jimeng-human-handoff.md` before writing detailed tool instructions.

Gate: stop after handoff and wait for the user to generate the video manually unless the user only asks for the prompt.

### 6. Returned Video Review

When the user returns a generated segment, review it before any next-segment design:

- inspect the original video or enough representative frames
- compare against the segment objective, storyboard images, prompt, and continuity bible
- classify the result as `可进入下一段`, `建议重跑`, or `必须重跑`
- record the actual ending state: final frame, character pose, direction, prop state, camera angle, lighting, and any drift
- extract constraints for the next segment prompt

If dialogue was required, explicitly check visible mouth movement, voice/accent fit, timing, and whether speech is on-screen rather than voice-over.

### 7. Next Segment Iteration

Design the next segment from the returned video's actual ending, not from the original imagined storyboard. Update:

- inherited opening frame and motion direction
- character and prop continuity notes
- revised segment beats
- new storyboard image prompts
- new video prompt with `@上一段视频` as the primary continuity reference

Repeat stages 3-7 until the full video is complete.

## Required Response Shape

For planning responses:

```markdown
**当前阶段**
<需求输入 / 脚本结构化 / 当前段分镜 / 即梦交接 / 成片回传检查 / 下一段设计>

**已确认**
- ...

**需要用户操作**
- ...

**本轮输出**
- ...

**一致性控制点**
- ...

**下一步**
- ...
```

For returned-video reviews:

```markdown
**判断**
可进入下一段 / 建议重跑 / 必须重跑

**通过项**
- ...

**问题项**
- ...

**实际结尾状态**
- ...

**下一段必须继承**
- ...

**下一步建议**
- ...
```

## Validation

Before claiming a segment is ready for video generation, check:

- current segment only; no premature later-segment storyboard generation
- character face, body, costume, voice/accent, and performance anchors are present
- storyboard prompts include action, frame role, direction, prop state, and negative constraints
- video prompt includes time beats, `@` references, continuity instructions, and failure checks
- human tool instructions are operational and do not imply automated Jimeng access

Before designing a next segment, check:

- previous generated video or representative frames were reviewed
- real ending state is recorded
- continuity changes are carried into the next storyboard and prompt
- drift risks are named rather than hidden
