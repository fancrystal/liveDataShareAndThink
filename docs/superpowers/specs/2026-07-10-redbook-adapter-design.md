# Redbook 真实数据适配器设计

状态：已确认，待实施  
确认日期：2026-07-10

## 目标

为一期内容引流平台增加只读的小红书关键词采集入口。它调用用户本机已登录状态下的 `redbook` CLI，转换搜索结果为现有的笔记、作者和指标快照领域模型。

## 边界

- 用户自行在本机 Chrome 登录小红书；应用不读取、上传、持久化 Cookie。
- 后端通过受限的子进程调用 `redbook search <keyword> --sort popular --json`，不执行任何发布、点赞、评论或收藏命令。
- 固定样本导入保留，继续作为测试和无登录环境下的演示路径。
- 一期不加入代理、验证码绕过、异步队列或自动重试。

## 架构

新增 `RedbookAdapter`，实现既有 `PlatformAdapter` 协议。适配器接收一个可注入的命令运行器，使用参数列表执行 CLI，解析 JSON 后映射到 `FixturePayload`。这样采集服务、数据库和分析模块无需知道 `redbook` 的命令或原始字段。

```
POST /api/projects/{id}/collections/redbook?keyword=...
  -> CollectionService
  -> RedbookAdapter
  -> redbook CLI（本机 Chrome 登录态）
  -> FixturePayload
  -> notes / authors / metric snapshots
```

## 错误契约

适配器将失败映射为明确的 HTTP 422：

- 命令不存在：提示安装 `@lucasygu/redbook`。
- CLI 退出失败且输出表明未登录、Cookie 过期、验证码或风控：提示用户在 Chrome 完成人工操作后重试。
- JSON 无法解析或缺少必须的笔记标识、作者、标题、链接、发布时间：提示 CLI 输出版本不兼容。

错误文本不包含 Cookie、环境变量或 CLI 的完整原始输出。

## 数据映射

兼容 `redbook` 当前搜索结果中常见的扁平字段与嵌套作者字段。笔记 ID、链接、标题、正文、类型、发布时间和互动量映射到现有 `CollectedNote`；无法取得的互动量与粉丝量保留为 `null`，不能伪造为 0。原始条目保存在既有 `raw_data` 中。

## 测试

单元测试通过注入假的命令运行器覆盖：成功标准化、缺少 CLI、未登录失败和无效 JSON。API 测试通过依赖替换验证真实导入路由与现有幂等写入链路。真实平台验证独立于测试套件，仅在用户已登录的本机手工执行。
