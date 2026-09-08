# 连接本地 Blender

用户要求建模或连接时，先运行 doctor；正常的只读检查和启动新受控实例不需要重复询问。工具层要求授权、安装 Add-on 或用户明确限定原窗口时，如实处理相应边界。

## 预检

Windows 优先运行不依赖 Python 的版本：

```powershell
powershell -ExecutionPolicy Bypass -File "<技能目录>/scripts/doctor.ps1" -BridgeDir "<已有桥接目录>"
```

已有可运行 Python 时也可使用：

```powershell
python "<技能目录>/scripts/doctor.py" --bridge-dir "<已有桥接目录>"
```

没有桥接目录时省略参数。检查 Python、Blender、FFmpeg、Blender 进程、目录可写性、同步/网络目录以及残留请求。拒绝访问表示查询失败，不表示软件或进程不存在。

## 复用连接

1. 读取项目中的 `blender_active_connection.json`，再检查其他明确属于当前项目的桥接目录。
2. 读取 `inflight.json`、`requests/` 和非终态 `states/`。有未解决工作时先按恢复指南处理。
3. 读取 `heartbeat.json`，但不把它当作执行证明。
4. 发送唯一 ID 的 `inspect_scene`：

```powershell
python "<技能目录>/scripts/send_blender_request.py" --bridge-dir "<桥接目录>" --operation inspect_scene --args-json '{"offset":0,"limit":100}'
```

只有收到该 ID 的 `completed` 响应才表示连接验证成功。

## 启动受控新实例

自动定位 Blender：进程可执行路径、项目记录、PATH、常见安装目录。然后执行：

```powershell
python "<技能目录>/scripts/start_connection.py" --blender "<blender.exe>" --project-dir "<项目绝对路径>"
```

启动器创建隔离桥接目录和随机令牌，打开交互式 Blender，完成只读检查后才写活动连接记录。保留用户原有窗口，不关闭未保存工程。

## 接入已经打开的窗口

自动启动脚本不能注入任意现有 Blender 窗口。需要接管现有窗口时：

1. 用 `prepare_connection.py` 创建私有桥接目录。
2. 在 Blender Preferences > Add-ons 中安装 `assets/junkun_blender_clay_bridge_addon.py`。
3. 在 3D View > Sidebar > Junkun 中选择准备好的目录并点击 **Start Trusted Local Bridge**。
4. 从 Codex 发送 `inspect_scene` 验证匹配响应。

这是一次明确的 Add-on 安装/启动步骤，不得声称 Skill 能绕过它。若用户不要求原窗口，优先启动新的受控实例。

## 边界

- 不自动安装 Blender、终止现有进程或丢弃未保存场景。
- bridge 目录不得位于网络共享、多人可写目录或不可信同步目录。
- 每个 bridge 目录只有一个 Blender 消费者和一个客户端。
- 启动失败先读 `logs/startup.log`、`launch.json`、`connected.json`、`inflight.json` 和请求状态，不能连续盲目启动。

