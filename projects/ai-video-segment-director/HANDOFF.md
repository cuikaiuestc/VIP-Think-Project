# Handoff

## What This Is

`ai-video-segment-director` is a Codex Skill for segment-by-segment AI video production. It is meant to preserve continuity across generated clips by forcing a review of each returned video before designing the next segment.

## Read First

1. `SKILL.md` for the main operating contract and mode selector.
2. `references/workflow.md` for the end-to-end loop.
3. `references/continuity-controls.md` for character, voice, mouth, prop, direction, and style consistency.
4. `references/jimeng-human-handoff.md` for manual Jimeng/Seedance operation boundaries.

## Key Decisions

- Input starts from a clear video requirement, not from a copied article or example.
- Only the current segment should receive storyboard image prompts.
- A generated segment must be returned and reviewed before the next segment is finalized.
- Jimeng/Seedance is manual for now. Future CLI/API integration should preserve the same handoff and review contracts.
- Face, costume, voice, mouth movement, props, direction, lighting, and style must be controlled in script, storyboard, prompt, and review layers.

## Developer Notes

- Keep `SKILL.md` concise. Put detailed rules in one-hop files under `references/`.
- Keep examples generic. Do not bake in private project names, article titles, or one-off characters.
- If adding automation, add a permission boundary before any upload, paid generation, or download step.
- If changing the workflow, update `test-prompts.json` and `scripts/validate_skill.py`.

## Validation Commands

```bash
python3 scripts/validate_skill.py
python3 -m json.tool test-prompts.json >/tmp/ai-video-segment-director-test-prompts.json
```

## Suggested Next Development

- Add a fixture-based response review if real output examples are collected.
- Add optional video frame extraction when a local video file is supplied.
- Add Jimeng CLI/API adapter only after upload, credit, and account boundaries are explicit.
