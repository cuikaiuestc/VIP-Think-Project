# AI Video Segment Director

`ai-video-segment-director` is a Codex Skill for producing AI-generated videos in controlled segments. It turns a clear video requirement into script structure, continuity anchors, storyboard image prompts, Jimeng/Seedance handoff prompts, returned-video review, and next-segment planning.

## Value

This skill converts ad hoc AI video prompting into a repeatable production workflow.

For external reporting, the value is:

- **Higher continuity quality**: each segment inherits from the actual returned video, not only from the original plan.
- **Lower rework cost**: drift is caught at segment boundaries before it contaminates later shots.
- **Reusable creative operations**: script, storyboard, prompt, handoff, and review are separated into clear artifacts.
- **Human-tool boundary clarity**: Jimeng/Seedance remains a manual operation until CLI/API integration exists, so paid generation is never hidden behind a false automation claim.
- **Cross-project portability**: the workflow starts from any explicit video requirement and does not depend on one article, case, character, or model provider.

## Workflow

1. Start from a clear video requirement.
2. Build the script structure and continuity bible.
3. Plan only the current segment.
4. Generate current-segment storyboard image prompts.
5. Produce a copy-ready Jimeng/Seedance handoff prompt.
6. Wait for the human to generate and return the original video.
7. Review the returned segment before designing the next segment.

## Installed Skill Layout

```text
ai-video-segment-director/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── scripts/validate_skill.py
├── test-prompts.json
├── VERSION
└── CHANGELOG.md
```

## Validation

Run:

```bash
python3 scripts/validate_skill.py
python3 -m json.tool test-prompts.json >/tmp/ai-video-segment-director-test-prompts.json
```

For Codex system skill validation, if PyYAML is not installed in system Python:

```bash
uv run --with pyyaml python /path/to/skill-creator/scripts/quick_validate.py .
```

## Current Boundary

This skill does not automate Jimeng/Seedance upload, credit spending, rendering, or download. It prepares the prompt and handoff instructions, then requires the generated video to be returned for review.
