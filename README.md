# LiveDataShareAndThink

面向小红书内容引流的分析与内容生产工作台。

当前里程碑使用固定样本打通：

> 研究项目 → 样本导入 → 相对表现分析 → 证据 → 选题 → 三版草稿 → 人工审核 → 导出

真实小红书登录和 `redbook` 适配器属于下一里程碑。

## 本地运行

### Docker Compose

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- Web：<http://localhost:5173>
- API：<http://localhost:8000/docs>

### 后端开发

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest backend\tests -v
```

如果默认 PyPI 在当前网络环境下载较慢：

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 前端开发

```powershell
npm.cmd --prefix frontend install
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend run dev
```

## 配置

复制 `.env.example` 为 `.env`。不要提交 Cookie、账号登录态或模型密钥。

### DeepSeek 内容生成

可以使用 DeepSeek。复制 `.env.example` 为 `.env` 后，只在 `.env` 中填写：

```ini
GENERATION_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_MODEL=deepseek-v4-flash
```

Key 由后端读取，浏览器端看不到；`.env` 已被 Git 忽略。未填写 Key 时，将使用本地模板生成器，仍可用于验证完整工作流。DeepSeek 使用官方 OpenAI 兼容接口 `https://api.deepseek.com/chat/completions`。

## 项目文档

- [项目方向](docs/PROJECT_DIRECTION.md)
- [第一期设计](docs/superpowers/specs/2026-07-09-xiaohongshu-content-growth-design.md)
- [固定样本闭环实施计划](docs/superpowers/plans/2026-07-09-fixed-sample-vertical-slice.md)
- [开源项目调研](docs/research/xiaohongshu-open-source-landscape.md)
