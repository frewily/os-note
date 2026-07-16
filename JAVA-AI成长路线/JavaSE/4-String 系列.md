# String 系列

---

## 一句话核心

String 不可变、StringBuilder 可变且快、StringBuffer 可变但慢还线程安全——日常写代码 90% 用 String，拼接用 StringBuilder。

---

## 为什么用

这个知识点的意义在于：**AI 生成的代码中用了什么，你要知道为什么**。

有时候 AI 会这样写：

```java
String result = "";
for (int i = 0; i < 1000; i++) {
    result += data[i];  // 每次循环都创建新 String 对象
}
```

这段代码能用，但效率极差。如果你看到 AI 在循环里用 `+=` 拼字符串，你要知道这里应该换成 `StringBuilder`。

反过来，如果 AI 用了 StringBuilder，你也要能看懂它在干什么。

---

## 关键理解

### String — 不可变

String 对象一旦创建，内容就不能变了。每次"修改"其实是创建了一个新对象。

```java
String s = "hello";
s = s + " world";  // 原 "hello" 没变，新创建了 "hello world"
```

不可变的好处：安全（不会被意外修改）、可以缓存（字符串常量池）、线程安全。

**在 vibe coding 中**：95% 的场景直接用 String 就够了，不用纠结。

### StringBuilder — 可变，单线程用

需要频繁拼接字符串时用。内部是一个可变的字符数组，拼接就是在数组后面追加，不创建新对象。

```java
StringBuilder sb = new StringBuilder();
sb.append("用户：").append(name).append("，余额：").append(balance);
return sb.toString();
```

**什么时候 AI 该用 StringBuilder：** 循环拼接、复杂拼接（多条数据组装）。

### StringBuffer — 可变，线程安全

和 StringBuilder 用法一模一样，方法上多了 `synchronized`。但实际项目中你几乎用不到——因为字符串拼接通常是在一个方法里完成的，不存在多线程竞争。

---

## 代码看一眼

```java
// ❌ 循环里 + 拼接（性能差，不要这样写）
String result = "";
for (String item : list) {
    result += item + ",";  // 每次循环都 new 一个 String
}

// ✅ 用 StringBuilder（AI 应该这样写）
StringBuilder sb = new StringBuilder();
for (String item : list) {
    sb.append(item).append(",");
}
String result = sb.toString();
```

**AI 生成的代码里**：你主要看循环拼接的地方用了什么方式。简单拼接（一两行）用 `+` 没问题，JVM 自己会优化成 StringBuilder。

---

## 你的项目里

| 场景 | 用哪个 | 为什么 |
|------|--------|--------|
| **URL 路径拼接**（如 API 地址） | String + | 简单拼接，JVM 会自己优化 |
| **日志拼消息** | String + 或 StringBuilder | 简单日志直接 +，复杂日志 AI 帮你写 StringBuilder |
| **HTTP 响应体拼装**（SSE 流式输出） | StringBuilder | 多条数据拼成一段文本发送给前端 |
| **拼接 SQL / Redis key** | String + 或 StringBuilder | 几个字符串拼接用 +，动态生成多条用 StringBuilder |

> **一句话总结**：不用记太多，记住"循环拼接用 StringBuilder，其他直接用 +"就够了。
