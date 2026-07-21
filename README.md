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

## 真实小红书关键词采集（本机可选）

固定样本流程不需要小红书登录。需要采集真实关键词样本时，请在本机准备：

```powershell
# Node.js 需要 22 或更高版本
npm.cmd install -g @lucasygu/redbook

# 在 Chrome 登录 https://www.xiaohongshu.com 后验证登录态
redbook.cmd whoami
```

Windows 的 PowerShell 可能会禁止执行 npm 生成的 `redbook.ps1`；此时请使用 `redbook.cmd`。如果登录检查提示没有 `a1` Cookie，请先确认 Chrome 已登录并能正常看到小红书首页；部分 Windows Chrome 版本还需要完全关闭 Chrome 后再重试。

随后调用只读采集接口：

```text
POST /api/projects/{project_id}/collections/redbook?keyword=敏感肌
```

服务端只启动本机 `redbook search` 并保存标准化的公开笔记、作者和指标快照；不会读取、上传或写入 Cookie，也不会执行发布、点赞、评论或收藏。未安装 CLI、登录过期、验证码或风控会返回 HTTP 422 和可执行提示。

## 一期主流程

1. 打开 `http://127.0.0.1:17777`，输入赛道关键词并点击“开始爆款研究”。
2. 系统只对本次采集到的公开搜索卡片做相对排名，最多展示 20 条；“今日”指本次采集日期，未知发布时间会明确标注。
3. 输入创作方向，生成标题、正文、标签和五页图文脚本。
4. 在结果底部预览五张 1080×1440 海报，可复制正文和标签，下载单张或全部 PNG 海报后人工审核发布。

小红书搜索结果属于公开页面可见样本，不等同于平台全站日榜。系统不自动发布，也不会绕过登录验证或平台风控。
