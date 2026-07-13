# HTTPS 与加密：你的数据是这样被保护的

> **模块**：模块六 · HTTPS 与加密  
> **日期**：2026-06-03  
> **工具**：curl + Wireshark（en0 网卡）  
> **目标**：https://www.baidu.com

---

## 一、实验：对比 HTTP vs HTTPS

用相同的工具（curl），访问不同的协议，抓包结果截然不同：

### HTTP 抓包（模块一）

```
TCP握手 →  GET / HTTP/1.1  →  HTTP/1.1 200 OK
           Host: httpbin.org        Content-Type: text/html
           User-Agent: Mozilla/...   ...
           Accept: */*               <html>...明文传输...</html>
```

**内容全部明文可见。** 请求头、响应头、响应体（HTML），任何人只要在中间抓包，就能看到你发了什么、收到了什么。

### HTTPS 抓包（本次实验）

```
TCP握手 →  Client Hello  →  Server Hello  →  Certificate  →  ...
                                                              ↓
                                                     Application Data（🔒 加密）
```

**内容全部加密。** 真正的 HTTP 请求/响应被包在 `Application Data` 里，Wireshark 无法解密。

---

## 二、抓包结果：你的 HTTPS 报文

```
No.    Time      Source → Dest         Protocol  Info
13590  243.828  客户端 → 服务器         TCP       [SYN]
13592  243.873  服务器 → 客户端         TCP       [SYN, ACK]
13593  243.873  客户端 → 服务器         TCP       [ACK]        ← TCP 握手完成
────────────────────────────────────────────────────────────────
13594  243.873  客户端 → 服务器         TLSv1.2   Client Hello (SNI=www.baidu.com)
13598  243.922  服务器 → 客户端         TCP       [ACK]
13600  243.926  服务器 → 客户端         TLSv1.2   Server Hello
13605  243.928  服务器 → 客户端         TLSv1.2   Certificate, Server Key Exchange,
                                                    Server Hello Done
...后续还有 Client Key Exchange → Change Cipher Spec → Encrypted Handshake Message → Application Data
```

### 报文分类

| 阶段 | 协议 | 报文 | 作用 |
|------|------|------|------|
| **TCP 握手** | TCP | SYN / SYN-ACK / ACK | 建立连接（和 HTTP 完全一样） |
| **TLS 握手** | TLSv1.2 | Client Hello | 客户端说：我支持的加密方式 |
| | TLSv1.2 | Server Hello | 服务器说：我们用这套加密 |
| | TLSv1.2 | Certificate | 服务器出示数字证书（身份证） |
| | TLSv1.2 | Server Hello Done | 服务器说：我这边好了 |
| | TLSv1.2 | Client Key Exchange | 客户端生成密钥，用服务器公钥加密后发过去 |
| | TLSv1.2 | Change Cipher Spec | 切换到加密模式 |
| | TLSv1.2 | Encrypted Handshake Message | 测试加密通道是否正常 |
| **加密传输** | TLSv1.2 | Application Data 🔒 | HTTP 请求/响应（完全加密） |

---

## 三、HTTPS 到底做了什么？

HTTPS = HTTP + **TLS**（Transport Layer Security，传输层安全协议）

TLS 要解决三个问题：

### 问题 1：怎么证明对方是真的？

```
你访问 https://www.baidu.com

你怎么确认给你发数据的真的是百度服务器，而不是中间人伪造的？

解决方案：数字证书（Certificate）
  ┌─────────────────────────────────┐
  │ 数字证书 = 服务器的身份证         │
  │                                 │
  │ 签发者：DigiCert / Let's Encrypt │
  │ 颁发给：www.baidu.com           │
  │ 有效期：2026-01-01 ~ 2027-01-01 │
  │ 公钥：xxxxxxxxxxxx              │
  │ 签名：CA 机构的数字签名           │
  └─────────────────────────────────┘
```

你的浏览器/curl 内置了受信任的 CA（证书颁发机构）列表，收到证书后验证签名——确认是百度，不是假的。

### 问题 2：加密的密钥怎么安全地传给对方？

```
如果直接用同一个密钥加密：
  你生成密钥 → 发给服务器 → 被中间人截获 → 加密失效 ❌

解决方案：混合加密（非对称 + 对称）
  
Step 1 - 非对称加密（握手阶段）：
  服务器把公钥发给客户端（通过 Certificate）
  客户端用公钥加密一个"对称密钥" → 发给服务器
  服务器用私钥解密 → 拿到对称密钥
  （即使被截获，没有私钥也解不开）

Step 2 - 对称加密（数据传输阶段）：
  双方用同一个"对称密钥"加密/解密数据
  （对称加密比非对称快 1000 倍，适合大量数据）
```

**一句话：** 非对称加密用来安全地交换对称密钥，对称加密用来高效地加密数据。

### 问题 3：数据会不会被篡改？

```
解决方案：消息认证码（MAC）

每个加密包后面附带一个校验值
接收方用密钥重新计算，如果对不上 → 数据被篡改了
```

---

## 四、TLS 握手完整流程（面试用）

```
客户端                              服务器
  │                                    │
  │──── TCP 三次握手 ─────────────→    │  建立 TCP 连接
  │                                    │
  │──── Client Hello ─────────────→    │  ① 客户端：我支持 TLS 1.3/1.2
  │    (TLS版本、加密套件列表)          │               AES-GCM、ChaCha20...
  │                                    │
  │←── Server Hello ─────────────────   │  ② 服务器：我们用 TLS 1.2 + AES-GCM
  │    (选定版本和加密套件)              │
  │                                    │
  │←── Certificate ──────────────────   │  ③ 服务器：这是我的数字证书
  │    (CA签名、公钥)                   │
  │                                    │
  │←── Server Hello Done ────────────   │  ④ 服务器：我这边好了
  │                                    │
  │──── Client Key Exchange ───────→    │  ⑤ 客户端：生成对称密钥，用公钥加密发送
  │                                    │
  │──── Change Cipher Spec ───────→    │  ⑥ 切换加密
  │──── Encrypted Handshake Msg ───→   │  ⑦ 测试加密通道
  │                                    │
  │←── Change Cipher Spec ──────────   │  ⑧ 服务器也切换加密
  │←── Encrypted Handshake Msg ─────   │  ⑨ 确认加密通道正常
  │                                    │
  │    ✅ TLS 握手完成                  │
  │                                    │
  │──── Application Data (加密) ───→   │  HTTP 请求 ❄️
  │←── Application Data (加密) ─────   │  HTTP 响应 ❄️
```

---

## 五、关键领悟

1. **HTTPS 不是新协议** — 就是 HTTP + TLS，TCP 三次握手之后、HTTP 数据之前，多了一层 TLS 握手
2. **数字证书的身份验证** — 确保和你通信的是真的服务器，不是中间人
3. **混合加密** — 非对称加密（握手时安全交换密钥）+ 对称加密（传输时高效加密数据）
4. **SNI 是明文的** — 你的抓包里 `Client Hello` 的 SNI（Server Name Indication）写了 `www.baidu.com`，这是明文的，所以中间人知道你访问了哪个网站
5. **从抓包看，HTTPS 比 HTTP 多了 1 个 RTT（往返时间）** — 如果你的连接是新建的，HTTPS 比 HTTP 慢约 100~200ms（TCP 1RTT + TLS 1~2RTT）

---

## 六、与后端的联系

| 你的后端工作 | 涉及的知识 |
|-------------|-----------|
| **配置 Nginx SSL 证书** | 理解 Certificate 链、私钥/公钥 |
| **JWT 签名** | 非对称签名（RS256）本质上就是证书签名技术的应用 |
| **OAuth2 / OIDC** | ID Token 用 JWT 签名，Access Token 传输需要 HTTPS |
| **SpringBoot 开启 HTTPS** | 本质上就是配置 keystore（证书+私钥） |
| **API 加密传输** | 什么时候该用 HTTPS、什么时候该额外加密 |

---

## 七、思考题

1. 你抓到的 `Server Hello` 报文里，服务器选了哪种加密套件？展开看一下 `Cipher Suite` 字段
2. 如果攻击者在你的电脑和百度之间做中间人攻击（MITM），HTTPS 能防住吗？什么情况防不住？
3. 为什么 `Client Hello` 里的 SNI（服务器名称）是明文的？这是设计缺陷还是有意的？

---

> **上一篇**：[[TCP拥塞控制：网络塞车了怎么办]]  
> **下一篇**：[[网络分层模型：一张图串起所有协议]]
