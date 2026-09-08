# Previs Review Loop

## Render Review Frames

为每个镜头选择开场、首次清晰构图、中点或揭示、动作/撞击帧和结束帧。发送结构化请求：

```powershell
python scripts/send_blender_request.py --bridge-dir "<bridge>" --operation render_review_frames --args-json '{"frames":[1,24,48,72],"output_dir":"D:/project/review/S01","resolution_x":1280,"resolution_y":720}' --timeout 120
```

渲染操作会恢复原帧、输出路径、分辨率、格式和渲染引擎。若指定的引擎不可用，结果包含警告。

## Contact Sheet

```powershell
python scripts/make_contact_sheet.py --input-dir "D:/project/review/S01" --output "D:/project/review/S01-contact.png" --columns 4 --max-frames 24
```

## Preview Video

先渲染连续帧，再按项目 FPS 编码：

```powershell
python scripts/encode_preview.py --input-dir "D:/project/review/S01" --output "D:/project/review/S01-preview.mp4" --fps 24
```

PNG 序列是可恢复的主预览产物，视频是派生产物。FFmpeg 不可用时仍交付 PNG；不要假装视频已经生成。

## Shot Manifest

时间线 camera marker 定义镜头起点，下一个 marker 的前一帧定义结束；最后一个镜头结束于场景结束帧。摄影机可保存 `shot_name`、`shot_purpose`、`camera_move` 和 `subject` 属性。

```powershell
python scripts/send_blender_request.py --bridge-dir "<bridge>" --operation export_shot_manifest --args-json '{"filepath":"D:/project/review/shot-manifest.json"}'
```

## Review Questions

- 主体是否立即可读，镜头是否完成唯一主要任务？
- 轴线、视线、运动方向和地理关系是否一致？
- 关键动作是否被遮挡、裁切或前景干扰？
- 焦段、机位高度和距离是否服务叙事？
- 摄影机是否有明确的起势、变化与落点？
- 碰撞、特效时点、缓动和角速度是否可信？

先修动作与碰撞，再修机位和目标，然后焦段构图、时间插值，最后才加抖动、尘土和闪光。每轮重渲染同一组帧，并记录可比较的具体变化。
