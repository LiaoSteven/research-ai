# API 文档

> **版本**: 1.0
> **最后更新**: 2025-10-17
> **项目**: research-ai

本目录包含项目所有 API 相关的技术文档。

---

## 📚 文档索引

### 1. [YouTube Data API 使用指南](youtube_api.md) 🔄 待完成
- YouTube Data API v3 配置
- API 密钥管理
- 配额与限制
- 数据采集最佳实践

### 2. [内部 API 端点文档](endpoints.md) 🔄 待完成
- RESTful API 设计
- 端点列表与功能
- 请求/响应格式
- 错误处理

### 3. [认证与授权](authentication.md) 🔄 待完成
- OAuth 2.0 流程
- API Token 管理
- 访问控制策略

---

## 🚀 快速开始

### YouTube Data API 基础配置

```python
# TODO: 示例代码待补充
from src.main.python.services.youtube_collector import YouTubeCollector

# 初始化收集器
collector = YouTubeCollector(api_key="YOUR_API_KEY")

# 获取视频评论
comments = collector.get_video_comments(video_id="VIDEO_ID")
```

---

## 📖 相关资源

- [YouTube Data API 官方文档](https://developers.google.com/youtube/v3)
- [Google API 配额管理](https://console.cloud.google.com/apis/dashboard)
- [项目开发指南](../dev/README.md)

---

## 📝 文档贡献

如需更新 API 文档，请遵循以下规范：

1. **清晰的示例代码** - 提供可运行的代码片段
2. **参数说明** - 详细说明所有参数类型和用途
3. **错误处理** - 列出可能的错误码和处理方法
4. **版本控制** - 标注 API 版本和变更历史

---

**项目主页**: [README.md](../../README.md) | **开发规范**: [CLAUDE.md](../../CLAUDE.md)
