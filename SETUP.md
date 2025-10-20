# 研究环境配置指南

## 🐍 Python 环境设置

### 步骤 1: 创建虚拟环境

```bash
# 在项目根目录
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac/WSL
# 或
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 步骤 2: 安装依赖

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt`，手动安装：

```bash
pip install python-dotenv google-api-python-client pandas numpy matplotlib seaborn scikit-learn transformers torch
```

### 步骤 3: 设置 API 密钥

创建 `.env` 文件（已完成）：

```
YOUTUBE_API_KEY=你的密钥
```

## 🚀 启动数据采集

### 在虚拟环境中运行：

```bash
# 确保已激活虚拟环境
source venv/bin/activate

# 运行采集
python src/main/python/services/natural_distribution_collector.py \
    --total 100000 \
    --start-date 2022-01-01 \
    --end-date 2025-10-31 \
    --output-dir data/raw
```

## ✅ 验证环境

```bash
python -c "import dotenv, googleapiclient; print('环境正常')"
```

## 📊 预期采集时间

- **小规模测试** (1,000条): ~5分钟
- **中规模** (10,000条): ~1小时
- **全规模** (100,000条): 数小时到1天（取决于API限流）

## ⚠️ 常见问题

### 问题 1: ModuleNotFoundError: No module named 'dotenv'

**解决**:
```bash
pip install python-dotenv
```

### 问题 2: API配额超限

**解决**:
- 等待配额重置（每日UTC 00:00）
- 使用 `--total` 参数减少目标数量进行测试

### 问题 3: 虚拟环境未激活

**症状**: 模块安装后仍报错

**解决**:
```bash
which python  # 应显示 venv 路径
source venv/bin/activate  # 重新激活
```

## 📁 项目结构

```
research-ai/
├── venv/                  # 虚拟环境（git忽略）
├── .env                   # API密钥（git忽略）
├── src/
│   └── main/python/
│       └── services/
│           └── natural_distribution_collector.py
├── data/
│   └── raw/              # 采集结果
└── requirements.txt      # Python依赖
```
