# AI 编码与 GitHub 敏感信息安全操作手册

> 适用范围：个人学习项目、课程项目、实习项目和工作项目。  
> 目标：防止 AI、IDE、脚本或人工操作把密码、API Key、Token、Cookie、私钥、个人信息和生产数据提交到 GitHub。

## 一、先记住四条底线

1. **真实秘密不进入源码、文档、测试数据、日志和 AI 对话。**
2. **AI 完成修改后，只能准备变更；提交和推送前必须经过人工检查与自动扫描。**
3. **GitHub Secret Scanning 是最后一道安全网，不能代替本地检查。**
4. **秘密一旦进入 Git 历史，就按已经泄露处理：先吊销或修改，再清理仓库。**

“仓库是私有的”“提交后马上删除”“Key 还没有被调用”都不能证明它没有泄露。私有仓库仍可能被协作者、自动化任务、恶意依赖或误配置访问；Git 历史也会保留已经删除的内容。

## 二、哪些内容不能提交

### 2.1 认证信息

- 密码、API Key、Access Token、Refresh Token、PAT
- Cookie、Session ID、JWT、验证码、登录请求样本
- SSH 私钥、TLS 私钥、助记词、证书私钥
- 数据库、Redis、消息队列、对象存储连接凭据
- 云服务密钥、支付密钥、Webhook Secret

### 2.2 个人及业务数据

- 学号、身份证号、手机号、住址、私人邮箱
- 未脱敏的用户表、订单、聊天记录、日志和数据库备份
- 学校或公司内部接口、内网地址、VPN 配置
- 带有账号信息的截图、抓包文件、浏览器导出文件

### 2.3 容易被忽视的载体

- `.env`、`application-local.yml`、`application-prod.yml`
- `.npmrc`、`.pypirc`、Maven `settings.xml`
- `*.pem`、`*.key`、`*.p12`、`*.jks`
- SQL、SQLite、CSV、Excel、压缩包和备份文件
- README、开发文档、AI 生成的示例、单元测试和 Mock 配置
- GitHub Actions 日志、构建产物、Issue、PR 评论和 Release 附件

## 三、每个新项目只需配置一次

### 3.1 使用环境变量

代码只读取变量名，不包含真实值：

```yaml
spring:
  datasource:
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}

external-api:
  api-key: ${EXTERNAL_API_KEY}
```

只提交模板文件：

```dotenv
# .env.example
DB_USERNAME=replace_me
DB_PASSWORD=replace_me
EXTERNAL_API_KEY=replace_me
```

真实值保存在本机 `.env`、IDE 的运行配置、操作系统密钥链、GitHub Actions Secrets 或公司的秘密管理系统中。

### 3.2 建立基础 `.gitignore`

按项目实际情况选用，不能机械覆盖仓库现有规则：

```gitignore
# Local secrets
.env
.env.*
!.env.example
*.local
application-local.yml
application-local.yaml
application-prod.yml
application-prod.yaml

# Keys and certificates
*.pem
*.key
*.p12
*.pfx
*.jks

# Local databases and backups
*.db
*.sqlite
*.sqlite3
*.bak
*.dump

# Tool-specific credentials
.npmrc
.pypirc
```

注意：`.gitignore` 只能阻止尚未被 Git 跟踪的文件。文件一旦进入过提交，后来再加入 `.gitignore` 不会清除历史。

### 3.3 给 AI 写仓库级安全规则

在仓库的 `AGENTS.md` 中加入：

```markdown
## Security rules

- Never place real passwords, API keys, tokens, cookies, private keys,
  personal identifiers, or production data in source code, documentation,
  tests, fixtures, examples, logs, issues, or commit messages.
- Use environment-variable names and redacted placeholders. Create only
  `.env.example`; never populate or stage `.env`.
- Do not read or print secret values. Report only the variable name and
  whether it is set.
- Do not run `git add -A`, create commits, or push until the user has reviewed
  the staged diff and the secret-scan result.
- Before proposing a commit, inspect `git status`, `git diff`,
  `git diff --cached`, and run the repository's secret scanner.
- If a secret may have entered Git, stop normal work and tell the user to
  revoke or rotate it before cleaning files or history.
```

这条规则应放在仓库里，由每次 AI 会话共同遵守。它不能代替扫描，但可以减少 AI 主动读取、复述和暂存秘密的概率。

### 3.4 安装秘密扫描器

macOS 可安装 Gitleaks：

```bash
brew install gitleaks
gitleaks version
```

首次接管已有项目时扫描工作区和 Git 历史：

```bash
gitleaks dir . --redact --no-banner
gitleaks git . --redact --no-banner
```

`--redact` 用于避免扫描报告再次显示完整秘密。不同版本的命令可能变化，升级后应先执行 `gitleaks --help` 核对。

### 3.5 启用 GitHub 保护

在 GitHub 仓库的 Security 或 Code security 设置中，启用平台提供的 Secret Scanning 和 Push Protection。组织或公司项目还应启用分支保护和必须通过的 CI 检查。

## 四、每次让 AI 写代码时的标准流程

### 阶段 A：开始开发前

- 告诉 AI 不得读取、打印或写入秘密值。
- 提供变量名和数据结构，不提供真实值。
- 用虚构的测试账号，例如 `student_demo_001`，禁止用真实学号充当 Mock 数据。
- 真实生产数据先脱敏，再用于调试。
- 确认 `.env`、本地配置、密钥文件已经被 `.gitignore` 排除。

推荐提示词：

```text
请完成这项开发，但必须遵守仓库 AGENTS.md 的安全规则。
所有凭据只使用环境变量名或明显的虚构占位符，不读取或输出真实值。
完成后先展示变更摘要、git diff 和秘密扫描结果，不提交、不推送。
```

### 阶段 B：AI 完成修改后

先检查有哪些文件发生变化：

```bash
git status --short
git diff --stat
git diff
```

重点检查：

- 是否新增 `.env`、本地配置、日志、数据库或备份文件；
- README、测试、Mock 数据中是否用了真实信息；
- 是否在异常信息和调试输出中打印请求头、Cookie、Token；
- 是否把前端变量当成秘密。浏览器中的前端代码和 `VITE_*`、`NEXT_PUBLIC_*` 等变量会发送给用户，不能保存私密 Key；
- 是否出现无法解释的长字符串、Base64 字符串或高随机度字符串。

### 阶段 C：只暂存确认过的文件

优先逐个暂存：

```bash
git add path/to/file1 path/to/file2
```

避免未经检查直接执行：

```bash
git add -A
git add .
```

检查即将提交的内容：

```bash
git diff --cached --stat
git diff --cached
```

暂存区是最终关口。工作区没有问题，不代表暂存区没有问题；反过来也一样。

### 阶段 D：扫描暂存内容和仓库

扫描暂存的补丁：

```bash
git diff --cached --binary | gitleaks stdin --redact --no-banner
```

扫描当前项目文件：

```bash
gitleaks dir . --redact --no-banner
```

发布公开仓库或正式版本前，再扫描完整历史：

```bash
gitleaks git . --redact --no-banner
```

扫描器通过不代表绝对安全。Gitleaks 擅长识别常见密钥，对学号、手机号、业务账号和项目自定义密文未必敏感，因此还要人工检查上下文。

### 阶段 E：人工确认后提交

确认以下项目全部满足后才提交：

- 暂存文件列表符合预期；
- 暂存 diff 已完整看过；
- 扫描结果通过，或每个告警都已人工确认；
- 没有真实个人信息、生产数据和凭据；
- 配置文件只包含环境变量和占位符；
- 提交信息本身不包含秘密或内部信息。

之后执行：

```bash
git commit -m "type: concise description"
```

推送前最后检查：

```bash
git status
git show --stat --oneline HEAD
git show --format=fuller --no-ext-diff HEAD
```

确认无误后再推送。

## 五、把检查做成强制门禁

### 5.1 本地提交钩子

可使用 `pre-commit` 框架或团队统一的 Git hook，在每次提交前运行 Gitleaks。钩子的原则是：扫描失败时退出码必须非零，从而阻止提交；扫描输出必须开启脱敏。

安装后需要实际做一次无秘密的测试提交，确认钩子确实运行。仅仅把配置文件放进仓库，不代表每位开发者的本地钩子已经安装。

### 5.2 CI 扫描

在 GitHub Actions 或公司 CI 中再次扫描。CI 应设置为合并前必须通过，并遵循以下规则：

- 不在日志里打印秘密值；
- 不把扫描报告作为公开附件上传；
- Fork PR 不获取生产 Secrets；
- 第三方 Action 固定到可信版本或提交 SHA；
- Workflow 使用最小 `permissions`；
- 生产部署使用独立环境和人工审批。

### 5.3 密钥本身也要限制损失

- 开发、测试、生产使用不同 Key；
- 为 Key 设置最小权限、调用额度、来源限制和过期时间；
- 能使用短期凭据时，不使用长期凭据；
- 为费用和异常调用设置告警；
- 定期轮换，离开项目时立即吊销；
- 不同服务不复用同一密码或 Key。

即使某个 Key 被误提交，这些限制也能显著缩小损失范围。

## 六、发现泄露后的应急流程

顺序非常重要：**先阻断凭据，再清理代码。**

1. **立即吊销或修改。** 不要先花时间删除 GitHub 文件；旧凭据必须立刻失效。
2. **检查使用记录。** 查看登录历史、API 调用、云账单、Token 权限和异常设备。
3. **生成新凭据。** 缩小权限和额度，不复用旧值。
4. **修复代码。** 改为环境变量或秘密管理系统，并补充 `.gitignore`。
5. **清理 Git 历史。** 使用经过审核的 `git filter-repo` 或平台流程重写历史；这会影响所有协作者，必须先备份并统一安排。
6. **检查其他传播位置。** 包括 Fork、PR、Issue、Actions 日志、Release、构建产物、包注册表和聊天记录。
7. **记录原因和改进。** 说明泄露入口、发现方式、影响范围以及新增的自动门禁。

删除当前文件、将仓库转为私有或重写历史，都不能让已经泄露的凭据重新变得安全，所以吊销或修改始终排在第一位。

## 七、常见误区

| 误区 | 实际风险 |
|---|---|
| “只是测试配置” | Mock、示例和文档最容易被误用真实凭据 |
| “Key 已经加密” | 密钥、IV 或解密代码同时提交时仍可恢复；弱编码不等于加密 |
| “仓库是私有的” | 私有仓库仍有协作者、CI、第三方应用和误配置风险 |
| “已经删除那一行了” | Git 历史、Fork、缓存和本地克隆可能仍然保存 |
| “GitHub 没报警” | 自定义凭据和个人信息可能不在检测规则中 |
| “AI 会替我检查” | AI 可能遗漏、误判，也可能把上下文中的秘密写回文件 |
| “扫描器显示通过” | 规则扫描无法理解所有业务数据和身份信息 |

## 八、个人项目的最小执行版本

如果不想一开始配置得太复杂，至少坚持下面六步：

```text
1. 真实秘密只放环境变量
2. 仓库只提交 .env.example
3. AI 不得直接提交或推送
4. 提交前完整查看 git diff --cached
5. 使用 Gitleaks 扫描暂存区和仓库
6. 发现泄露立即吊销，再清理 Git 历史
```

## 九、提交前一分钟检查清单

- [ ] 我没有把真实密码、Token、Cookie、API Key 或私钥交给 AI
- [ ] `git status --short` 中没有意外文件
- [ ] `.env`、本地配置、数据库、日志和备份没有被暂存
- [ ] 文档、测试、Mock 和截图没有真实个人信息
- [ ] 我完整查看了 `git diff --cached`
- [ ] Gitleaks 扫描通过，告警已逐条确认
- [ ] 前端代码中没有需要保密的 Key
- [ ] 提交信息没有秘密和内部信息
- [ ] 这是公开项目时，我已经扫描 Git 历史
- [ ] 我确认后才允许 AI 提交或推送

## 十、推荐的固定协作口令

以后可以直接对 AI 说：

```text
按安全提交流程完成本次修改：遵守 AGENTS.md，不读取或输出真实秘密，
只暂存本次明确修改的文件；提交前展示 git status、暂存 diff 摘要和
脱敏后的秘密扫描结果。未经我明确确认，不提交、不推送。
```

这句话适合日常使用，但仓库中的规则、自动扫描和人工确认仍需同时保留。
