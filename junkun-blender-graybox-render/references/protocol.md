# Bridge Protocol v2

文件桥接是本机可信传输，不是安全沙箱。所有路径都相对于独立 bridge 目录。

## Layout

```text
bridge/
├── bridge.py
├── bridge_config.json
├── connected.json
├── heartbeat.json
├── inflight.json
├── requests/<id>.json
├── archive/requests/<id>.json
├── archive/cancelled_requests/<id>.json
├── states/<id>.json
├── state_history/<id>.jsonl
├── responses/<id>.json
├── cancellations/<id>.json
├── backups/*.blend
└── logs/
```

## Request

```json
{
  "protocol": 2,
  "id": "uuid",
  "created_at": 1770000000.0,
  "expires_at": 1770000060.0,
  "kind": "operation",
  "operation": "inspect_scene",
  "args": {"offset": 0, "limit": 200},
  "code": null,
  "code_sha256": null,
  "high_risk": false
}
```

`kind=code` 时必须包含 UTF-8 `code`、匹配的 SHA-256 和 `high_risk=true`。客户端只有在命令行明确传入 `--allow-high-risk-code` 后才创建此类请求。

## States

- `queued`: 客户端已经发布请求，仍可尝试由取消客户端原子取得所有权。
- `accepted`: Blender 已将请求原子移动到归档目录并取得所有权。
- `running`: 即将执行结构化操作或高风险代码。
- `completed`: 执行完成并产生成功响应。
- `failed`: 校验、预检或执行失败。
- `cancelled`: Blender 在进入 `running` 前发现取消标记。

终态不可逆。取消客户端与 Blender 通过原子移动竞争 queued 请求；取消客户端成功取得请求时才报告保证取消。`accepted` 之后的取消仅为尽力而为，`running` 中的 Python 不能安全抢占；执行结束后仍以实际结果进入 `completed` 或 `failed`。

## Structured Operations

- `inspect_scene`: 分页返回场景与对象摘要；只读。
- `save_copy`: 保存 `.blend` 副本；参数 `filepath`。
- `upsert_camera`: 创建或修改摄影机和 target。支持 `location`、`lens_mm`、`clip_start`、`clip_end`、`sensor_width`、`target_location`、`start_frame`、`end_frame`、`marker_name` 与 `keyframes`；设 `use_target=false` 时可用 `rotation_euler`。
- `render_review_frames`: 将指定帧渲染为 PNG；参数 `frames`、`output_dir`，可选分辨率和引擎。
- `export_shot_manifest`: 根据摄影机 marker 和摄影机自定义属性输出 JSON；参数 `filepath`。

桥接自动将 `upsert_camera` 和高风险代码视为场景修改。场景修改执行前必须成功写出安全副本，并尝试创建 undo checkpoint。

## Invariants

- 一个 bridge 目录只允许一个 Blender 消费者和一个客户端。
- 请求入队后不可修改；SHA-256 不匹配必须失败。
- Blender 必须以原子移动取得并归档请求，再把请求标记为 `accepted`；取消客户端可用同样方式取得仍处于 queued 的请求。
- 响应使用 `responses/<id>.json`，不得复用单一 `response.json`。
- `connected.json` 是启动记录；`heartbeat.json` 也只能说明轮询近期运行。真正的可用性仍由匹配 ID 的只读响应证明。
- 超时后先查询状态，不能自动重试修改请求。
