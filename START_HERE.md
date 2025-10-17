# 快速开始指南

## ✅ 环境已配置完成

您的 API 密钥已设置并测试成功！

## 🚀 开始采集数据

### 方式 1：从热门视频自动采集（推荐）

```bash
# 激活虚拟环境
source venv/bin/activate

# 采集 1000 条评论
python collect_trending.py

# 或指定类别
python collect_trending.py --category gaming
python collect_trending.py --category music
python collect_trending.py --category tech
```

### 方式 2：从指定视频采集

1. 编辑 `video_urls.txt`，添加视频链接
2. 运行：
```bash
source venv/bin/activate
python collect_sample.py
```

## 📊 采集结果

数据将保存在：
- `data/raw/comments_*.json` - 评论数据
- `data/raw/videos_*.json` - 视频元数据

## 🔑 关于 YouTube Data API

- **您的 API 密钥**: 已在 `.env` 文件中配置
- **每日配额**: 10,000 单位
- **评论采集成本**: 约 1 单位/请求
- **预计可采集**: 约 9,000 条评论/天

## 📝 常用命令

```bash
# 1. 激活环境（每次开始工作时）
source venv/bin/activate

# 2. 测试 API
python quick_test.py

# 3. 采集数据
python collect_trending.py --max-comments 1000

# 4. 退出虚拟环境
deactivate
```

## 🆘 遇到问题？

1. API 密钥错误：检查 `.env` 文件
2. 配额超限：等待第二天重置
3. 库未安装：运行 `pip install google-api-python-client python-dotenv`

## 📖 详细文档

查看 `INSTALL.md` 了解更多详情。
