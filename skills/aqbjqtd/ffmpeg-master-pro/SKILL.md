---
name: ffmpeg-master-pro
description: "FFmpeg Master Pro - 全能视频处理技能。当用户需要视频处理时使用，支持视频转换、视频压缩、视频编辑等。当用户要求视频处理, 视频转换, 视频压缩, FFmpeg, 视频编辑, 视频转码, 视频剪辑, 字幕处理, 视频优化, 批量视频处理, GIF转换, 视频翻转, 速度调节, 音频提取, 视频合并, 宽高比, 水印, 截图, 抽帧时使用此技能。"
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires":
          { "bins": ["ffmpeg", "ffprobe", "python3"] },
        "install":
          [
            {
              "id": "apt-ffmpeg",
              "kind": "apt",
              "packages": ["ffmpeg", "python3"],
              "bins": ["ffmpeg", "ffprobe", "python3"],
              "label": "Install FFmpeg + Python (apt)",
            },
            {
              "id": "brew-ffmpeg",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg", "ffprobe"],
              "label": "Install FFmpeg (brew)",
            },
          ],
      },
  }
---

# FFmpeg Master - 全能视频处理技能

## 核心工作流

技能提供 14 个核心工作流，覆盖所有常见的视频处理场景。

### 工作流 1：智能转码与压缩
触发条件："压缩""转码""格式转换""减小文件"
- 输入分析：检测源视频格式、编码、分辨率、码率、时长
- 码率计算：三模型融合（分辨率/复杂度/目标大小）
- GPU 检测：自动检测并使用可用的硬件加速
- 参数优化：根据内容类型选择最优编码预设
- 执行转换：构建并执行 FFmpeg 命令
- 质量验证：对比转换前后质量，验证文件大小

[详细工作流文档 →](references/detailed_workflows.md#工作流1：智能转码与压缩)

### 工作流 2：智能参数优化
自动识别 6 种视频类型并优化编码参数
- 屏幕录制、动漫、体育、音乐视频、电影、老旧视频
- 基于内容特征（运动幅度、场景复杂度、色彩分布）分析
- 自动选择最优编码参数（Codec、Preset、CRF、Tune）
- GPU 加速优化（NVIDIA NVENC、AMD AMF、Intel QSV）
- 质量偏好调整（高质量/平衡/快速编码）

[详细工作流文档 →](references/detailed_workflows.md#工作流2：智能参数优化)

### 工作流 3：预设模板系统
内置 8+ 预设模板，覆盖主流平台和场景
- youtube, bilibili, wechat, douyin
- social_media, archival, preview, web_optimized

[详细工作流文档 →](references/detailed_workflows.md#工作流3：预设模板系统)

### 工作流 4：精确文件大小控制
使用两遍编码实现精确文件大小控制（偏差 < 5%）
- 智能码率计算：基于目标大小、视频时长、音频码率
- 自适应优化：多次迭代调整码率
- 质量感知压缩：可选的质量评估（PSNR/SSIM/VMAF）

[详细工作流文档 →](references/detailed_workflows.md#工作流4：精确文件大小控制)

### 工作流 5：Smart Cut 混合剪辑
智能剪辑策略，平衡速度与质量
- 自动检测关键帧位置
- 三种剪辑模式：快速模式、精确模式、Smart Cut 混合模式
- 自动音视频同步修复
- 剪辑点质量评估

[Smart Cut 详细指南 →](references/smart_cut_guide.md)

### 工作流 6：关键帧分析
智能分析视频关键帧，优化剪辑策略
- 关键帧时间轴导出（JSON/CSV/Markdown/TXT）
- 剪辑点质量评估（excellent/good/fair/poor）
- 智能分段策略建议

[关键帧分析详细指南 →](references/keyframe_analysis.md)

### 工作流 7：字幕处理
完整的字幕处理功能
- 提取字幕（支持所有格式）
- 嵌入字幕（软字幕）
- 烧录字幕（硬字幕）
- 转换字幕格式

[详细工作流 →](references/detailed_workflows.md#工作流5：字幕处理)

### 工作流 8：滤镜与特效
滤镜、旋转、水印叠加等视觉效果
- 水印叠加（多位置支持）
- 视频旋转（90°/180°/270°）
- 帧翻转（hflip/vflip）

[详细工作流 →](references/detailed_workflows.md#工作流6：滤镜与特效)

### 工作流 9：GIF 转换
将视频片段转换为高质量 GIF 动图
- 自定义帧率和分辨率
- 精确时间范围裁剪
- 调色板优化（高色彩保真度）
- 文件大小控制

[详细工作流 →](references/detailed_workflows.md#工作流9gif转换)

### 工作流 10：翻转与镜像
水平/垂直翻转视频画面
- 水平翻转（左右镜像）
- 垂直翻转（上下镜像）
- 组合翻转（180°旋转）
- 流复制，无重编码

[详细工作流 →](references/detailed_workflows.md#工作流10翻转与镜像)

### 工作流 11：速度调节
视频加减速与慢动作
- 加速（2x/4x/10x 延时摄影）
- 慢动作（0.5x/0.25x）
- 音频同步调速
- 极端速度链式处理

[详细工作流 →](references/detailed_workflows.md#工作流11速度调节)

### 工作流 12：音频提取与移除
独立的音频轨道操作
- 提取音频为 MP3/AAC/WAV/FLAC/OGG
- 移除音频（静音视频）
- 音频编码参数自定义

[详细工作流 →](references/detailed_workflows.md#工作流12音频提取与移除)

### 工作流 13：视频合并
将多个视频片段拼接为一个
- 自动生成 concat 文件列表
- 流复制快速合并
- 智能参数归一化（不同编码/分辨率的视频）
- 批量合并支持

[详细工作流 →](references/detailed_workflows.md#工作流13视频合并)

### 工作流 14：宽高比调整
调整视频画面比例，带黑边填充
- 常见比例：16:9 / 4:3 / 1:1 / 9:16 / 21:9
- 自定义分辨率
- 保持原始比例填充黑边
- 无黑边裁剪模式

[详细工作流 →](references/detailed_workflows.md#工作流14宽高比调整)

## 智能决策系统

### 内容类型识别
技能会自动识别视频内容类型并优化参数：

| 内容类型 | 编码器 | 预设 | CRF | 码率控制 |
|---------|-------|------|-----|---------|
| 电影/电视剧 | x264 | slow | 23 | VBR |
| 动画/动漫 | x264 | medium | 20 | VBR |
| 屏幕录制 | x264 | veryfast | 18 | CBR |
| 体育/运动 | x264 | fast | 22 | VBR |
| 音乐视频 | x264 | medium | 21 | VBR |

[优化算法详解 →](references/optimization_guide.md)

### GPU 加速检测
技能会自动检测并使用可用的硬件加速：
- **NVIDIA**：NVENC (H.264/H.265/AV1)
- **AMD**：AMF (H.264/H.265)
- **Intel**：QSV (H.264/H.265/VP9)

### 质量验证
技能会自动验证输出质量：
- 文件大小、分辨率、码率、时长
- 音视频同步性、文件完整性
- 高级验证：VMAF 评分、SSIM 指标、PSNR 值

## 详细文档

### 核心参考
- **Smart Cut 完整指南**：[Smart Cut 指南](references/smart_cut_guide.md)
- **关键帧分析指南**：[关键帧分析](references/keyframe_analysis.md)
- **最佳实践**：[最佳实践](references/best_practices.md)
- **详细工作流**：[详细工作流](references/detailed_workflows.md)
- **快速入门**：[快速入门](references/quickstart.md)
- **API 参考**：[API 参考](references/api_reference.md)
- **优化算法详解**：[优化指南](references/optimization_guide.md)
- **故障排除**：[故障排除](references/troubleshooting.md)

### 配置文件
预设配置：`assets/presets/`
- youtube.json, bilibili.json, wechat.json, douyin.json
- social_media.json, archival.json, preview.json, web_optimized.json

## 技术要求

**系统要求：**
- Python 3.7+
- FFmpeg 4.0+ (必须安装并添加到 PATH)
- 足够的磁盘空间（至少是源视频的 2 倍）

**可选依赖：**
- NVIDIA GPU + CUDA（NVENC 加速）
- AMD GPU + AMF 运行时
- Intel QSV 运行时
- VMAF 库（质量评估）

**安装 FFmpeg：**
```bash
# Windows (使用 winget)
winget install FFmpeg

# macOS (使用 Homebrew)
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install ffmpeg

# 验证安装
ffmpeg -version
```

📖 **完整安装指南**：[快速入门](references/quickstart.md)

---

**FFmpeg Master** - 让视频处理变得简单智能！
