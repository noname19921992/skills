# Local Bridge Operations

只有在没有可用的标准 Blender MCP/结构化工具时才使用此文件桥接。完整协议见 [protocol.md](protocol.md)。

## Prepare

```powershell
python scripts/prepare_connection.py --bridge-dir "<private-local-dir>" --project-dir "<project-dir>"
```

脚本创建协议目录、随机 token、`bridge_config.json` 和绑定该目录的 `bridge.py`。不要直接运行 assets 中的模板。

## Submit Structured Operations

```powershell
python scripts/send_blender_request.py --bridge-dir "<bridge>" --operation inspect_scene --args-json '{"offset":0,"limit":200}'
```

保存副本：

```powershell
python scripts/send_blender_request.py --bridge-dir "<bridge>" --operation save_copy --args-json '{"filepath":"D:/project/revisions/scene_v002.blend"}'
```

客户端输出请求 ID。超时后用 `request_status.py` 查询，不得直接重复提交。

## High-Risk Python

只有结构化操作确实不足时才使用：

```powershell
python scripts/send_blender_request.py --bridge-dir "<bridge>" --code-file "<reviewed.py>" --allow-high-risk-code
```

代码内容会计算 SHA-256；Blender 执行前重新校验。此标记不是沙箱或授权替代品。代码仍拥有 Blender 进程权限，必须来自可信、已审查来源。

## Safety Properties

- 请求原子入队并在执行前归档。
- 每个请求拥有独立状态历史和响应。
- 修改场景前自动保存 `.blend` 安全副本；失败则中止修改。
- 桥接尝试创建 undo checkpoint，但后台模式或特定上下文可能不支持 undo；响应会记录结果。
- 随机 token 用于避免跨项目误投递，不能防御已经能读取桥接目录的恶意进程。
- 长时间外部 I/O 不得在 Blender 主线程执行。

