# 发布到博客（Obsidian → WordPress）

笔记库通过 GitHub Actions 在每次备份 push 后，自动把**标记过**的笔记同步到博客
http://freblog.frewily.top/ 。

## 怎么标记一篇笔记要发布

在笔记**最顶部**加 YAML frontmatter（文件第一行必须是 `---`）：

```markdown
---
publish: true
title: "可选：显示标题（不填则用第一个 # 标题）"
description: "可选：文章摘要"
tags:
  - Java
  - Spring
---

# 正文
```

- 只有 `publish: true` 的笔记才会被同步；没有标记的笔记绝不会离开 GitHub。
- `title` / `description` / `tags` 都是可选的。`tags` 会映射成博客的 WordPress 标签（不存在会自动创建）。
- `publish` 必须是布尔值 `true`。写成 `"true"`（字符串）不会生效。

## 批量标记（一次标记整个目录）

不想手动一篇篇加 `publish: true`？用仓库里现成的脚本一键批量加：

```bash
# 标记整个目录下所有笔记
python3 scripts/mark_publish.py "JAVA-AI成长路线"

# 只标记某个模块（比如以后新增的模块）
python3 scripts/mark_publish.py "JAVA-AI成长路线/Redis"

# 先预览会标记哪些文件，不写盘
python3 scripts/mark_publish.py "JAVA-AI成长路线" --dry-run
```

- 脚本默认排除个人/元笔记（如 `规划/`、`JVM/`、`项目复盘/`、`复习追踪表.md`、所有 `规则说明.md`、空文件）。
- 想额外排除某些文件：追加 `--exclude "相对路径"`。
- 已带 `publish: true` 的文件不会被重复修改，正文一律不动。
- 批量标记后记得 **push**（Obsidian Git: Push 或等每日自动备份），才会触发同步。

## 自动分类（按文件夹）

发布到博客时，文章会自动归入 WordPress 分类，分类名取自笔记在仓库里的**模块文件夹**（无需在 WP 后台手动建分类）：

| 笔记路径 | 博客分类 |
|---------|---------|
| `JAVA-AI成长路线/Docker/1-镜像与容器.md` | `Docker` |
| `JAVA-AI成长路线/JavaSE/并发/3-线程池.md` | `JavaSE`（嵌套的并发/集合归到所属模块） |
| `JAVA-AI成长路线/算法套路/回溯/46-全排列.md` | `算法套路` |
| `JAVA-AI成长路线/00-知识地图.md` | `JAVA-AI成长路线` |

规则：取 `JAVA-AI成长路线/` 下的**第一层文件夹**作为分类；直接在 `JAVA-AI成长路线/` 根目录下的笔记归到顶层分类。
重跑同步会自动给已发布的旧文章补上分类，URL 不变。

## 同步时机

- 每次 obsidian-git 自动备份 push 到 GitHub 后，GitHub Actions 会自动跑同步。
- 想立刻同步：Obsidian 里 `Ctrl/Cmd+P` → "Obsidian Git: Push"。
- 也可以去 GitHub 仓库 → Actions → "Blog Sync" → Run workflow 手动触发。

## 行为约定

| 操作 | 结果 |
|------|------|
| 编辑一篇已发布的笔记 | 更新博客上**同一篇文章**，URL 不变，不产生重复 |
| 给新笔记加 `publish: true` | 创建一篇新文章 |
| 删除 `publish: true` 标记 | 博客文章**保留**，只是不再更新（状态里标记为 retired） |
| 删除笔记文件 | 博客文章**保留** |
| 重命名 / 移动已发布的笔记 | **会创建一篇新文章**，旧文章变孤儿（链接失效） |

> 重命名已发布笔记前请三思，或用手动方式处理旧文章。

## 同步流程（原理）

```
┌─────────────┐  ① obsidian-git 自动备份   ┌──────────┐  ③ GitHub Actions 触发   ┌──────────┐
│  Obsidian   │ ─────────────────────────> │  GitHub  │ ─────────────────────> │ WordPress │
│  （本地笔记） │     每天 commit + push      │  私有仓库  │                         │  博客     │
└─────────────┘                           └──────────┘   ② 跑 blog_sync.py      └──────────┘
```

1. **标记**：笔记 frontmatter 加 `publish: true`，只有标记过的笔记才会被同步。
2. **推送**：obsidian-git 每天自动 commit + push 到 GitHub（记录形如 `vault backup: 2026-08-03 20:08:15`）。
3. **触发**：GitHub Actions 监测到 push 触及 `**.md`，就在云上虚拟机里装依赖、跑同步脚本。
4. **同步**（`scripts/blog_sync.py` 全量扫描、幂等、自愈）：
   - **过滤**：扫描整个仓库所有 `.md`，只保留带 `publish: true` 的。
   - **比对**：每篇算内容 MD5，跟上次同步状态 `.blog-sync-state.json` 对比：
     - 没变 → `[skip]`（省 API 请求）
     - 变了 → `[UPDATE]` 更新同一篇文章
     - 没见过 → `[CREATE]` 新建文章
   - **渲染**：Markdown → HTML，同时处理 wiki-link（`[[xxx]]` 变成文章真实 URL 的超链接）和本地图片（上传到 WP 媒体库）。
   - **发布**：调 WordPress REST API（应用密码 Basic Auth），`POST /posts` 建文章、`POST /categories` 建分类、`POST /tags` 建标签。
   - **回写**：把每篇文章的 `wp_id` / URL / MD5 存回 state 文件。
   - **两遍渲染**：新文章发布前 URL 未知，先按预测 URL 创建；拿到真实 URL 后把所有已发布文章重渲染一遍，让跨文章链接收敛。
5. **收尾**：workflow 把更新的 state 文件提交回仓库（`.json` 不触发 `**.md` 过滤，不会无限循环）。

**为什么不会重复发文章？** 靠 state 文件里的 `wp_id` + MD5：每次全量扫描，没变的直接跳过，改过的用 `wp_id` 走更新而不是新建。

## 首次部署（一次性设置）

> 以下三步需要你手动完成，脚本和 workflow 已经就位。

### 1. WordPress 允许 http 下的应用密码

你的博客是 `http://`（无 HTTPS），而 WordPress 默认只允许 HTTPS/localhost 使用
Application Passwords。用 Code Snippets 插件（或 `wp-content/mu-plugins/` 下放一个 php 文件）
加一行：

```php
add_filter( 'wp_is_application_passwords_available', '__return_true' );
```

### 2. 创建应用密码

wp-admin → 用户 → 个人资料 → 拉到 "Application Passwords" → 名称填 `github blog sync` →
创建 → 复制生成的密码（**空格也是密码的一部分**，形如 `abcd efgh ijkl mnop`）。

### 3. 存进 GitHub Secrets

仓库 `frewily/os-note` → Settings → Secrets and variables → Actions → New repository secret：

| Secret 名 | 值 |
|-----------|-----|
| `WP_BASE_URL` | `http://freblog.frewily.top` |
| `WP_USER` | WordPress 登录用户名 |
| `WP_APP_PASSWORD` | 上一步复制的应用密码 |

### 4. 验证

在本地验证凭据：

```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/blog_sync.py --vault . --check-auth \
  --base-url "$WP_BASE_URL" --user "$WP_USER" --password "$WP_APP_PASSWORD"
```

看到 `auth OK: <用户名>` 就说明通了。然后给一两篇笔记加上 `publish: true`，push 触发
workflow，去博客确认文章发布成功。

## 本地预览（不发网络请求）

```bash
.venv/bin/python scripts/blog_sync.py --vault . --dry-run --base-url http://freblog.frewily.top
```

会打印「计划创建/更新/跳过」清单，不会调用任何 API。

## 恢复 / 故障排查

- 同步状态存在仓库根目录 `.blog-sync-state.json`（记录每篇笔记对应的 WordPress 文章 ID）。
  它随每次同步自动提交，git 历史里可恢复：`git checkout <commit> -- .blog-sync-state.json`，
  然后手动 Run workflow 重新同步。
- 某次 workflow 红了？去 Actions 看日志。常见原因：Secrets 没配、应用密码被撤销、
  或 WP 服务器临时 5xx。修复后重新 Run workflow（全量扫描会自愈）。
- 私有仓库 GitHub Actions 免费额度 2000 分钟/月，每次运行约 1-2 分钟，可忽略。

## 已知限制

- 博客是纯 http，应用密码走 Basic Auth 在网络上可被嗅探。个人博客风险可接受；
  长期建议上 HTTPS（如 Cloudflare 代理），上 HTTPS 后可去掉第 1 步的过滤器。
- Obsidian 专属语法：callout（`> [!note]`）会渲染成普通引用块；`==高亮==` 原样显示。
- 笔记里的本地图片会自动上传到博客媒体库；远程图片原样保留。
