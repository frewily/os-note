# ConcurrentHashMap

---

## 核心

ConcurrentHashMap 是线程安全的 HashMap，采用细粒度锁机制实现高并发读写。

---

## 为什么需要它

```java
HashMap        → 线程不安全，并发 put 可能数据覆盖
Hashtable      → 线程安全，但全表加锁，性能极差
ConcurrentHashMap → 线程安全，锁粒度细，高并发场景的首选
```

---

## 线程安全原理（JDK 8）

JDK 8 的 ConcurrentHashMap 与 HashMap 结构相同（数组 + 链表 + 红黑树），通过不同策略保证线程安全：

| 场景 | 策略 |
|------|------|
| bucket 为空 | CAS 无锁插入 |
| bucket 非空 | synchronized 锁头节点 |
| 扩容中 | 多线程协同扩容 |

**为什么读操作不用加锁**：Node 的 `val` 和 `next` 用 `volatile` 修饰，保证一个线程的修改对其他线程立即可见。

---

## 核心用法

```java
// 创建
ConcurrentHashMap<String, Object> cache = new ConcurrentHashMap<>();

// 常用 API
cache.put("key", value);           // 写入
Object val = cache.get("key");     // 读取
cache.putIfAbsent("key", value);   // 不存在才写入（原子操作）
cache.remove("key");              // 删除

// 遍历
cache.forEach((k, v) -> { ... });  // 安全遍历
```

---

## vibe coding 视角

- 看到多线程环境中的 Map 操作，应使用 ConcurrentHashMap 替代 HashMap
- API 用法与 HashMap 几乎一致，切换成本极低
- 不需要记忆底层 Segment 分段锁等历史实现，JDK 8 版本足够覆盖日常使用

---

## 关联知识点

- [[index]] — 返回知识地图
- [[集合/1-HashMap]] — ConcurrentHashMap 是 HashMap 的线程安全版本
- [[并发/1-synchronized 原理]] — JDK 8 使用 synchronized 锁头节点保证线程安全

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **在线用户状态管理** | 多线程 Web 服务器中管理用户会话状态 |
| **分布式锁计数器** | 配合 Redis 做限流时，ConcurrentHashMap 维护本地计数 |
| **黑马点评秒杀场景** | 高并发写入的 Map 应使用 ConcurrentHashMap |
