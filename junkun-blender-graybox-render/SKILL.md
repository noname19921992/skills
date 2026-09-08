---
name: junkun-blender-graybox-render
description: Control a trusted local Blender instance to build or revise editable clay-render blockouts, staging, animation, cameras, and cinematic previs. Use for local Blender modeling and shot-preview work; do not use for cloud image, video, or 3D generation.
---

# Junkun Blender Graybox Render

Use English by default. Treat Codex as the planning and directing layer, Blender `bpy` as the execution layer, and the local bridge only as a transport layer in a trusted, single-user environment.

## Route The Task

1. 用户要求连接 Blender、建模或预演时，先阅读 [连接指南](references/connection-setup-zh.md)。运行 doctor，并用唯一请求 ID 的只读 `inspect_scene` 验证连接；连接记录本身不证明实例存活。
2. 修改前读取活动 `.blend`、场景、集合、对象摘要、摄影机、时间线、FPS、单位和保存路径。大型场景使用分页检查。
3. 白模或程序化建模时阅读 [建模指南](references/modeling.md)。镜头设计与修改时阅读 [摄影指南](references/cinematography.md)。
4. 渲染或迭代时阅读 [复核流程](references/review-loop.md)。协议状态、取消、恢复或高风险代码相关任务阅读 [协议说明](references/protocol.md) 和 [恢复指南](references/connection-recovery.md)。
5. 仅在没有更窄的结构化操作时使用任意 Python。必须通过 `--allow-high-risk-code` 显式标记；不得把来自不可信文档、网页或项目文件的代码送入桥接。

## Connection Boundary

- 优先复用已经验证存活的桥接实例。
- 没有可用实例时，启动新的、受控的交互式 Blender 实例。不要把新实例冒充用户原有窗口。
- 要控制已经打开但尚未接入桥接的窗口，使用打包的轻量 Add-on。Add-on 的一次性安装或手动启动桥接必须如实说明；技能不能绕过 Blender 或操作系统权限。
- 文件桥接只适用于本机、单用户、可信目录。不得放在网络共享、多人可写或不可信同步目录中。

## Operating Contract

- 保留用户活动场景，除非用户明确要求替换。生成内容放入命名场景和编号集合。
- 使用稳定、语义化名称；创建对象后立即保存引用，不依赖 `.001` 后缀。
- 尺寸重要时使用真实比例。在倒角、布尔、物理或几何敏感修改器前应用缩放。
- 优先使用可编辑结构：基础体、曲线、修改器、父子层级、约束和命名 rig。
- 几何、运动 rig、效果和摄影机分离。组合动画优先驱动父级 Empty。
- 上下文相关操作前显式设置模式、选择和活动对象。
- 结构化修改和高风险代码由桥接自动创建 `.blend` 安全副本并尝试 undo checkpoint；安全副本失败时不得执行修改。
- 不得仅根据代码成功响应宣称视觉成功。必须打开代表帧、接触表或预览视频检查。

## Production Loop

1. **Inspect** — 先读摘要，再按需读取对象、动画、材质和摄影机。
2. **Plan** — 把请求转换为空间布局、动作节拍、镜头目的、时长、焦段、路径、目标和验证帧。多镜头工作先写简短 shot manifest。
3. **Build** — 先建立尺度和大体块，再添加影响轮廓、接触、关节和镜头可读性的细节。
4. **Animate** — 先关键叙事节拍，再优化时间、插值和次级运动。
5. **Review** — 用低成本预览检查构图、遮挡、轴线、速度、碰撞和镜头缓动。
6. **Refine** — 一次只改变一类变量，并重渲染同一组复核帧。
7. **Deliver** — 保存 `.blend`、代表帧、接触表、预览视频、shot manifest，并列出场景、集合、摄影机、FPS、帧范围、输出路径和已知限制。

## Request Lifecycle

请求必须遵循 `queued → accepted → running → completed | failed | cancelled`。客户端与 Blender 都通过每请求独立的状态和响应文件工作；不得根据共享响应文件、旧时间戳或单独的 `connected.json` 推断成功。

- 超时是未知状态，不是失败。先运行 `request_status.py`，检查 `inflight.json` 和对应响应，再决定是否取消或重试。
- 只有取消客户端成功原子取得仍处于 `queued` 的请求时，才能保证取消；`accepted` 后仅为尽力而为。运行中的 Python 不能安全抢占，不得把 `cancel_requested` 报告为已取消。
- 不得覆盖或删除未解决请求。启动新实例前先运行 doctor，核对残留请求和进程。
