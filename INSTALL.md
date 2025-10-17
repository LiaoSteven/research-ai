# Installation Guide

## Quick Start

### Option 1: Minimal Installation (Recommended to start)

Install only core dependencies needed for data collection and basic analysis:

```bash
pip install -r requirements-minimal.txt
```

**What's included:**
- YouTube data collection
- Data preprocessing
- Simple sentiment analysis (rule-based)
- LDA topic modeling
- Basic visualization

### Option 2: Full Installation (For advanced ML)

Install all dependencies including transformers and BERTopic:

```bash
pip install -r requirements-full.txt
```

**Additional features:**
- BERT-based sentiment analysis
- Advanced topic modeling (BERTopic)
- Time-series analysis (Prophet)
- Jupyter notebooks
- Development tools

### Option 3: Custom Installation

1. Start with minimal:
   ```bash
   pip install -r requirements-minimal.txt
   ```

2. Add components as needed:
   ```bash
   # For transformers-based sentiment analysis
   pip install torch>=2.0.0 transformers>=4.30.0

   # For BERTopic
   pip install bertopic>=0.16.0 sentence-transformers>=2.2.0

   # For Jupyter notebooks
   pip install jupyter jupyterlab
   ```

---

## System Requirements

- **Python**: 3.8 or higher (3.9+ recommended)
- **OS**: Linux, macOS, or Windows
- **RAM**: Minimum 4GB, 8GB+ recommended for transformers
- **Disk Space**: ~2GB for full installation

---

## Setup Steps

### 1. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
# Choose one:
pip install -r requirements-minimal.txt  # Basic
pip install -r requirements-full.txt     # Complete
```

### 3. Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your YouTube API key
# YOUTUBE_API_KEY=your_api_key_here
```

### 4. Verify Installation

```bash
# Run quickstart example
python examples/quickstart.py
```

---

## Troubleshooting

### Issue: torch installation fails

**Solution:** Install PyTorch separately first:
```bash
# Visit https://pytorch.org/get-started/locally/ for platform-specific commands
# Example for CPU-only:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue: numpy version conflicts

**Solution:** Upgrade pip and try again:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements-minimal.txt
```

### Issue: Google API authentication errors

**Solution:**
1. Ensure YOUTUBE_API_KEY is set in .env
2. Check API quota at https://console.cloud.google.com/apis/dashboard
3. Enable YouTube Data API v3 in Google Cloud Console

### Issue: BERTopic installation fails

**Solution:** Install sentence-transformers first:
```bash
pip install sentence-transformers
pip install bertopic
```

---

## Platform-Specific Notes

### Windows
- Use `venv\Scripts\activate` to activate virtual environment
- If you get execution policy errors, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### macOS
- Install Xcode Command Line Tools if needed:
  ```bash
  xcode-select --install
  ```

### Linux (WSL)
- Ensure build tools are installed:
  ```bash
  sudo apt-get update
  sudo apt-get install build-essential python3-dev
  ```

---

## GPU Support (Optional)

For faster transformers inference with CUDA:

```bash
# Check CUDA version
nvidia-smi

# Install PyTorch with CUDA support
# Example for CUDA 11.8:
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

## Verification Checklist

After installation, verify everything works:

- [ ] Import test: `python -c "from src.main.python.core.config import get_config"`
- [ ] YouTube collector: Check API key is configured
- [ ] Run quickstart: `python examples/quickstart.py`
- [ ] Check installed packages: `pip list | grep -E "(pandas|numpy|scikit-learn)"`

---

## Next Steps

1. Configure your YouTube API key in `.env`
2. Read the [User Guide](docs/user/README.md)
3. Try the [Quick Start Example](examples/quickstart.py)
4. Start collecting data with `scripts/collect_data.py`

---

## Getting Help

- Check [Troubleshooting Guide](docs/user/troubleshooting.md)
- Review [API Documentation](docs/api/README.md)
- Open an issue on GitHub

---

**Note:** Start with `requirements-minimal.txt` for faster installation and fewer dependencies. Add advanced features only when needed.
