# Continuity Controls

Use this reference when building the continuity bible, storyboard prompts, video prompts, or returned-video checks.

## Layered Control Model

Control consistency in every layer:

| Layer | What To Lock | How To Express It |
|---|---|---|
| Script | identity, role, motivation, speech style | character bible and dialogue rules |
| Segment plan | start/end state, direction, prop status | inherited state and target state |
| Storyboard image | face, body, costume, pose, space | concrete visual anchors and negative constraints |
| Video prompt | time beats, references, movement, speech | `@` references, time codes, camera/action instructions |
| Review | actual drift and usable ending | pass/retry decision and next carry-over notes |

## Character Consistency

Always specify:

- approximate age and life texture
- face shape, hair, skin, body type, posture, and gait
- costume layers, fabric texture, color, footwear, and accessories
- emotional range and performance style
- what must not change: no younger version, no costume swap, no beauty retouch, no different body shape

If a role image exists, state that it is the primary identity reference. If the user has generated a previous segment, state that the returned video becomes the strongest continuity reference.

## Voice And Mouth Consistency

When speech is required:

- state whether the line is voice-over or on-screen character speech
- if on-screen, require visible mouth/lip movement and a face angle that can support it
- specify language, dialect, accent, age of voice, speaking volume, and emotional tone
- keep the line short enough for the segment length
- check whether audio sounds like the same person across segments

Use hard wording when needed: "这句必须是画面中的角色本人开口说话，有可见口型，不是旁白，不是画外音，不是后期配音。"

## Space And Direction Consistency

Lock:

- which side key buildings, roads, fields, windows, doors, vehicles, or furniture occupy
- direction of travel, such as moving away from camera, left-to-right, or from kitchen to field
- camera relation to subject, such as following behind, side tracking, handheld close-up
- entrance/exit points and where the next segment should begin

Reject or warn about storyboard images that reverse direction or swap key landmarks when the scene is continuous.

## Prop And State Continuity

Record prop state before and after each segment:

- basket empty, half-full, or full
- clothing wet or dry
- object in left or right hand
- food raw, washed, cooked, or served
- door open/closed, light on/off, pot steaming/not steaming

Use prop state in negative prompts: "不要让篮子一开始就装满菜" or "不要让锅从空锅跳到已经盛好的粥".

## Lighting And Style Consistency

Lock:

- time of day and weather
- color temperature and saturation
- realism level, such as documentary, handheld, natural light
- lens feel and camera stability
- texture level, such as ordinary life vs. commercial polish

Repeat style constraints in each segment. Do not rely on the first prompt to carry style forever.

## Review Checklist

After every returned video, check:

- same person or identity drift
- same costume and accessories
- same voice/accent and speech mode
- same location logic and direction of travel
- prop state continuity
- lighting and weather continuity
- ending frame usability for next segment
- whether any defect is acceptable, requires prompt adjustment, or requires rerun
