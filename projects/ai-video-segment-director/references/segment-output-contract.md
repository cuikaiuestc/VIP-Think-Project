# Segment Output Contract

Use this reference when producing user-facing artifacts for each segment.

## Production Brief

```markdown
**视频目标**
- ...

**平台与规格**
- 比例：
- 总时长：
- 单段时长：
- 工具：

**故事核心**
- ...

**角色锚点**
- 人物：
- 外貌：
- 服装：
- 声音/口音：
- 表演方式：

**世界锚点**
- 场景：
- 时间/天气：
- 色彩/镜头：

**非目标**
- ...
```

## Segment Storyboard

```markdown
**第 N 段：<time range / duration>**

**本段目标**
- ...

**继承自上一段**
- ...

**结束时必须留下**
- ...

**分镜图设计**
1. `@图片1`：<opening beat>
2. `@图片2`：<process beat>
3. `@图片3`：<landing beat>

**一致性风险**
- ...
```

## Storyboard Image Prompt

```markdown
### @图片1 - <frame role>

用途：控制 <opening/process/landing/speech>。

提示词：
<subject identity>, <action>, <environment>, <composition>, <camera>, <lighting>, <style>, <prop state>, <continuity anchors>.

负面约束：
不要换人，不要换衣服，不要改变方向，不要改变天气，不要商业广告感，不要文字水印，不要畸形手。
```

## Jimeng Video Prompt

```markdown
@视频1 负责上一段连续性，@图片1 负责开场，@图片2 负责过程，@图片3 负责结尾落点。

基于 @视频1 继续扩展第 N 段，不是重新开场。请严格继承上一段里的同一个人物、同一套服装、同一环境、同一光线、同一镜头质感。

本段为 <10/15> 秒，内容是：<one-sentence segment action>。

00:00-00:03：...
00:03-00:06：...
00:06-00:10：...

整体要求：...

负面约束：不要换人，不要换衣服，不要改变行进方向，不要让道具状态跳变，不要现代城市背景，不要强烈广告打光，不要字幕，不要 logo，不要水印。
```

## Returned Video Review

```markdown
**判断**
可进入下一段 / 建议重跑 / 必须重跑

**对齐项**
- ...

**偏移项**
- ...

**实际结尾状态**
- 人物：
- 姿态：
- 道具：
- 场景：
- 镜头方向：
- 光线：

**下一段必须继承**
- ...

**下一段提示词要修正**
- ...
```

## Failure Language

Use direct but operational wording:

- "这版不能进入下一段，因为方向已经反了，继续用会扩大穿帮。"
- "这版可以进入下一段，但下一段提示词必须锁住衣服颜色和篮子状态。"
- "这版适合做口型测试，但不适合作为最终片段。"
