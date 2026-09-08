# Connection Diagnosis and Recovery

## Establish Facts

1. 运行 doctor，定位真实 bridge 根目录和 Blender 进程。不要根据目录名或文件修改时间猜测。
2. 读取 `bridge_config.json`、`connected.json`、`heartbeat.json`、`inflight.json`、`requests/`、`states/`、`responses/` 和 `archive/requests/`。
3. 对每个非终态请求运行：

```powershell
python scripts/request_status.py --bridge-dir "<bridge>" --request-id "<id>"
```

4. `queued` 代表尚未确认接收；`accepted` 代表 Blender 已归档并取得所有权；`running` 代表代码可能正在改变场景。
5. 只有匹配 ID 的终态响应可以证明请求结果。渲染完成还必须打开输出检查视觉质量。

## Cancellation

```powershell
python scripts/cancel_request.py --bridge-dir "<bridge>" --request-id "<id>"
```

- `queued` 请求只有在取消工具成功原子取得请求文件并返回 `guaranteed=true` 时才保证取消。
- `accepted` 请求的取消是尽力而为；如果 Blender 已越过取消检查，它仍会进入 `running`。
- `running` 请求只会记录取消意图；Blender 主线程中的 Python 不能安全强制中断。
- 不得把取消意图当成 `cancelled` 终态。等待实际 `completed` 或 `failed`，或确认 Blender 进程已经终止后人工恢复。

## Stale Inflight

若 `inflight.json` 存在但对应 PID 不再运行，先保存该文件和状态历史作为诊断记录。检查 `.blend`、自动备份和输出文件，确定是否发生部分修改。只有确认消费者已经停止后，才可将请求人工标记为失败并移走 stale inflight；不要在 Blender 仍可能执行时清理。

若 `client.lock` 残留，先检查其中 PID。只有确认该客户端进程已停止，并且没有正在发布的临时请求文件时，才能移走锁文件；锁存在本身不是删除授权。

## Timeout

客户端超时返回退出码 2，表示未知结果。按顺序检查：

1. `request_status.py`；
2. `inflight.json` 与 Blender PID；
3. `responses/<id>.json`；
4. 预期输出和 `backups/`；
5. Blender system console 与 `logs/`。

修改请求不得自动重试。若原请求进入 `failed` 或确认从未运行，才创建新 ID 重试。

## Existing Window Limitation

未安装或未启动 Add-on 的既有窗口无法由文件桥接自动接管。使用打包 Add-on 明确接入，或者启动新的受控实例；不得将新实例描述成原窗口。
