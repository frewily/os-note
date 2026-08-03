---
publish: true
---

# TCP 三次握手：我用 Java 亲手建立了一条连接

> **模块**：模块三 · TCP 三次握手  
> **日期**：2026-06-02  
> **工具**：Java Socket + Wireshark  
> **端口**：8888

---

## 一、Java Socket 代码

### Server.java

```java
import java.net.*;
import java.io.*;

public class Server {
    public static void main(String[] args) throws IOException {
        ServerSocket serverSocket = new ServerSocket(8888);
        System.out.println("服务器已启动，等待连接...");

        Socket socket = serverSocket.accept();
        System.out.println("客户端已连接：");

        BufferedReader reader = new BufferedReader(
                new InputStreamReader(socket.getInputStream())
        );
        String message = reader.readLine();
        System.out.println("收到消息：" + message);

        reader.close();
        socket.close();
        serverSocket.close();
    }
}
```

### Client.java

```java
import java.net.*;
import java.io.*;

public class Client {
    public static void main(String[] args) throws IOException {
        Socket socket = new Socket("127.0.0.1", 8888);

        PrintWriter writer = new PrintWriter(socket.getOutputStream(), true);
        writer.println("Hello Server");

        socket.close();
    }
}
```

---

## 二、抓包结果

在 Wireshark 中监听 `lo0`（回环地址），过滤 `tcp.port == 8888`，抓到 10 个报文：

### 三次握手

```
① 65082 → 8888  [SYN]      Seq=0
② 8888  → 65082 [SYN, ACK] Seq=0  Ack=1
③ 65082 → 8888  [ACK]      Seq=1  Ack=1
```

### 数据传输

```
④ 65082 → 8888  [PSH, ACK] Seq=1  Ack=1  Len=13  ← "Hello Server\n"
⑤ 8888  → 65082 [ACK]      Seq=1  Ack=14         ← 确认 13 字节已收到
```

### 四次挥手

```
⑥ 65082 → 8888  [FIN, ACK] Seq=14 Ack=1
⑦ 8888  → 65082 [ACK]      Seq=1  Ack=15
⑧ 8888  → 65082 [FIN, ACK] Seq=1  Ack=15
⑨ 65082 → 8888  [ACK]      Seq=15 Ack=2
```

---

## 三、三次握手详解（核心）

### 3.1 为什么是三次？

```
客户端                         服务器
  │                              │
  │──── ① SYN (Seq=0) ──────→   │  客户端：我要连你
  │                              │
  │←── ② SYN, ACK (Seq=0, Ack=1)─│  服务器：好的，我准备好了
  │                              │
  │──── ③ ACK (Seq=1, Ack=1)─→   │  客户端：收到，连接建立
  │                              │
  │        ✅ 连接建立成功         │
```

**三次握手要证明**：双方的发送能力和接收能力都正常。

| 步骤 | 证明了什么 |
|------|-----------|
| ① 客户端发送 SYN | 客户端的发送能力 OK |
| ② 服务器回复 SYN-ACK | 服务器的接收能力 OK + 发送能力 OK |
| ③ 客户端回复 ACK | 客户端的接收能力 OK |

> 如果只握两次手，服务器无法确认客户端是否收到了自己的 SYN-ACK（即客户端的接收能力）。

### 3.2 SEQ 和 ACK 的含义

```
SEQ = 当前发送的数据是第几个字节
ACK = 已经收到对方前 N-1 个字节，期待下一个字节从第 N 个开始
```

用对话类比：

```
① 客户端："我从 0 号开始说"                       [SYN]   Seq=0
② 服务器："我从 0 号开始说。你的0号收到了，下一个请从1号说"  [SYN,ACK] Seq=0 Ack=1
③ 客户端："好的。你的0号收到了，下一个请从1号说"           [ACK]   Seq=1 Ack=1
```

### 3.3 握手中的 SEQ/ACK 变化

| 方向 | Flag | Seq | Ack | 含义 |
|------|------|-----|-----|------|
| 客户端→服务器 | SYN | **0** | — | 客户端从 0 号开始 |
| 服务器→客户端 | SYN, ACK | **0** | **1** | 我也从 0 号开始，已收到你的 0 号 |
| 客户端→服务器 | ACK | **1** | **1** | 下个从 1 号说，已收到你的 0 号 |

---

## 四、数据传输中的 SEQ/ACK

```
客户端                                     服务器
  │                                          │
  │──── PSH, ACK (Seq=1, Ack=1, Len=13) ──→  │  发送 "Hello Server"
  │                                          │
  │←── ACK (Seq=1, Ack=14) ────────────────  │  确认 13 字节已收到
  │                                          │
```

**Seq + Len = 下一个 Seq**

```
发送前  Seq=1
发送了  Len=13 字节
发送后  Seq=1 + 13 = 14   ← 下一次发送从 14 号开始
```

对方回复的 `Ack=14` 表示："你发到 13 号的字节我都收到了，下次请从 14 号开始发"。

> 这就是 TCP 可靠传输的核心机制：**每个字节都有编号，通过 Seq 和 Ack 的配合，确保数据不丢、不乱序。**

---

## 五、SEQ/ACK 速查

| 事件 | 谁→谁 | Seq | Ack | 含义 |
|------|-------|-----|-----|------|
| 发起连接 | 客户端→服务器 | 0 | — | 初次打招呼 |
| 接受连接 | 服务器→客户端 | 0 | 1 | 回应 + 确认 |
| 确认连接 | 客户端→服务器 | 1 | 1 | 确认完成 |
| 发送数据 | 客户端→服务器 | 1 | 1 | 字节 1~13 |
| 确认数据 | 服务器→客户端 | 1 | 14 | 字节 1~13 已收齐 |
| 主动关闭 | 客户端→服务器 | 14 | 1 | FIN 也要消耗序号 |
| 确认关闭 | 服务器→客户端 | 1 | 15 | 确认 FIN |
| 被动关闭 | 服务器→客户端 | 1 | 15 | 服务器也发起 FIN |
| 最终确认 | 客户端→服务器 | 15 | 2 | 完成关闭 |

---

## 六、关键领悟

1. **TCP 是面向连接的** —— 通信前必须先三次握手建立连接
2. **TCP 是可靠传输的** —— 通过 SEQ/ACK 的编号机制保证数据完整
3. **每个字节都有编号** —— Seq 不是"第几个包"，而是"第几个字节"
4. **握手也要消耗序号** —— SYN 和 FIN 各占一个序号
5. **全双工通信** —— 两边可以同时收发，关闭时也要各自独立关闭（四次挥手）

---

---

## 附录：TCP 标志位（Flags）速查

> 本文首次提到，后续模块会深入。作为独立知识点，可与后续笔记交叉链接。

### 什么是 TCP 标志位

TCP 报文头部中有一组 **Flags（标志位）**，每个标志位是一个比特（0 或 1），用来表示这个报文的目的或类型。

```
TCP Flags（共 9 位，常用的 6 个）：
┌───┬───┬───┬───┬───┬───┐
│ U │ A │ P │ R │ S │ F │
│ R │ C │ S │ S │ Y │ I │
│ G │ K │ H │ T │ N │ N │
└───┴───┴───┴───┴───┴───┘
```

### 六个常用标志位

| 标志 | 全称 | 含义 | 出现场景 |
|------|------|------|---------|
| **SYN** | Synchronize | 同步 — "我想建立连接" | 三次握手第①步 |
| **ACK** | Acknowledgment | 确认 — "我收到了" | 除第①步外几乎每个包都有 |
| **SYN+ACK** | — | "我同意连接" | 三次握手第②步（两个标志同时为 1） |
| **FIN** | Finish | 结束 — "我想关闭连接" | 四次挥手 |
| **PSH** | Push | 推送 — "让上层立即处理" | 发送数据时 |
| **RST** | Reset | 重置 — "出错了，强制断开" | 连接异常中断 |

### 在 Wireshark 中查看

双击任意 TCP 报文，展开 `Transmission Control Protocol` → `Flags`，可以看到每个标志位的开关状态：

```
Flags: 0x002 (SYN)
    .... .... ..1. = Syn: Set (1)      ← SYN=1
    .... .... ...0 = Fin: Not set (0)  ← FIN=0
```

三次握手的三个包在 Wireshark 中的标志位状态：

| 步骤 | Flags 十六进制 | SYN | ACK | 作用 |
|------|--------------|-----|-----|------|
| ① SYN | 0x002 | 1 | 0 | 发起连接 |
| ② SYN, ACK | 0x012 | 1 | 1 | 确认 + 同意连接 |
| ③ ACK | 0x010 | 0 | 1 | 确认完成 |

> **关联笔记**：[后续模块会深入 PSH、RST 等标志位]

---

### 🧪 实战发现：握手后多出的 Window Update 报文

在本次抓包中，你实际抓到了 **10 个报文**，比笔记中列出的 9 条多了 1 条：

```
第④行  8888 → 65082  [TCP Window Update] [ACK]  Seq=1  Ack=1
```

**为什么会有这个包？**

三次握手时，双方在 SYN 中带的窗口大小是初始值（65535）。握手完成后，双方需要**更新实际的接收窗口大小**以告知对方自己的真实接收能力。

```
三次握手：    ① SYN → ② SYN-ACK → ③ ACK
窗口更新：    ④ Window Update ACK     ← 实际存在的报文
数据传输：    ⑤ PSH → ⑥ ACK
四次挥手：    ⑦ FIN → ⑧ ACK → ⑨ FIN → ⑩ ACK
```

**验证方法**：对比握手和窗口更新报文的 Win 字段

| 报文 | Win 字段 | 说明 |
|------|---------|------|
| ① `[SYN]` | 65535 | 初始窗口（未协商缩放因子） |
| ② `[SYN, ACK]` | 65535 | 服务器初始窗口 |
| ③ `[ACK]` | **408320** | 客户端更新实际窗口 |
| ④ `[Window Update]` | **408320** | 服务器更新实际窗口 |

> 大部分教材和面试只讲 9 步流程，实际 TCP 实现会在握手后发送窗口更新报文。**你亲手抓到了一条"教材没写"的真实报文**，这就是动手实践的价值。

## 七、思考题

1. 为什么不用两次握手？如果只用两次会有什么问题？
2. 如果第三次握手的 ACK 丢了，会发生什么？
3. 如果把 `Len=13` 改成发送更长的消息，Seq 和 Ack 的变化规律还一样吗？

---

> **上一篇**：[[DNS解析：从域名到IP发生了什么]]  
> **下一篇**：[[TCP四次挥手与可靠传输]]
