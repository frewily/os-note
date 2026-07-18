# String 系列

---

## 核心

String 不可变，StringBuilder 可变（单线程快），StringBuffer 可变（线程安全慢）。

---

## String — 不可变

**定义**：String 对象创建后内容不可变，每次"修改"都创建新对象。

```java
String s = "hello";
s = s + " world";  // 原 "hello" 不变，创建新对象 "hello world"
```

**价值**：不可变性带来线程安全、字符串常量池复用、缓存安全（如 HashMap key）。

**实际用法**：95% 的场景直接用 String。简单拼接（非循环）由 JVM 自动优化为 StringBuilder，无需手动处理。

---

## StringBuilder — 可变，单线程专用

**定义**：可变的字符序列，内部是动态数组，追加操作不创建新对象。

```java
StringBuilder sb = new StringBuilder();
sb.append("用户：").append(name).append("，余额：").append(balance);
return sb.toString();
```

**适用场景**：循环拼接、多条数据动态组装。

---

## StringBuffer — 可变，线程安全

与 StringBuilder API 完全相同，方法上加了 `synchronized`。

**适用场景**：理论上用于多线程环境下的字符串操作。实际项目中几乎用不到——字符串拼接通常在一个方法内完成，不存在线程竞争。

---

## 选择依据

| 场景 | 选用 |
|------|------|
| 普通字符串操作（非循环拼接） | String |
| 循环拼接、复杂组装 | StringBuilder |
| 极罕见的跨线程共享拼接 | StringBuffer |

**vibe coding 视角**：AI 生成的代码若在循环中使用 `+=` 拼接字符串，应理解为低效写法，需替换为 StringBuilder。

---

## 关联知识点

- [[3-== 与 equals]] — 字符串常量池机制直接影响 == 的比较结果

---

## 项目关联

| 场景 | 选用 | 原因 |
|------|------|------|
| URL / Redis key 拼接 | String + | 简单拼接，JVM 自动优化 |
| SSE 流式输出响应体拼装 | StringBuilder | 多条数据逐一追加 |
| 日志消息组装 | String + | 级别简单，编译器自优化 |
