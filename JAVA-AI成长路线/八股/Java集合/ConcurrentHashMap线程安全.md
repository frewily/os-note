---
publish: true
---

# ConcurrentHashMap 线程安全原理

> 参考资料：JavaGuide、掘金、CSDN 等多源整合

---

## 关联知识点

- [[八股/八股笔记]] — 八股笔记汇总
> 面试价值：⭐⭐⭐⭐⭐

---

## 为什么需要 ConcurrentHashMap？

| 实现类 | 线程安全 | 锁机制 | 问题 |
|--------|---------|--------|------|
| HashMap | ❌ | 无 | 多线程数据覆盖 / 死循环 |
| Hashtable | ✅ | 全表 synchronized | 性能极低，同一时刻只能一个线程操作 |
| ConcurrentHashMap | ✅ | 分段锁 / CAS+synchronized | 高并发首选 |

ConcurrentHashMap 的设计目标：**在保证线程安全的前提下，最大化并发效率**。核心思路是"缩小锁粒度"。

---

## JDK 1.7：Segment 分段锁

### 数据结构

```
ConcurrentHashMap
 ├── Segment[0]  ← 继承 ReentrantLock（一把锁）
 │    ├── HashEntry[0] → 链表A
 │    ├── HashEntry[1] → 链表B
 │    └── ...
 ├── Segment[1]  ← 另一把锁
 ├── Segment[2]  ← ...
 └── ...（默认 16 个 Segment）
```

### 线程安全怎么实现

- 写操作时，只锁数据所在的 **一个 Segment**（继承了 ReentrantLock）
- 不同 Segment 的线程可以**同时执行**，互不阻塞
- 默认 16 个 Segment → 理论并发度 16

### 缺点

1. **并发度上限固定**：最多 16 个线程同时写，改不了
2. **锁粒度仍偏粗**：一个 Segment 内部的所有操作还是串行
3. **Segment 本身是额外对象**，浪费内存

---

## JDK 1.8：CAS + synchronized

### 数据结构改变

抛弃了 Segment，直接用和 HashMap 一样的结构：

> **Node 数组 + 链表 + 红黑树**

```
ConcurrentHashMap
 ├── Node[0]  ← synchronized 锁头节点
 │    └── 链表/红黑树
 ├── Node[1]
 ├── Node[2]
 └── ...
```

### 线程安全怎么实现（三种情况）

| 场景 | 策略 | 为什么这么干 |
|------|------|-------------|
| **桶为空** | **CAS 无锁插入** | 预期值是 null，竞争少，CAS 足够 |
| **桶不为空** | **synchronized 锁头节点** | 只锁这一个桶，其他桶完全不受影响 |
| **扩容中** | **多线程协助扩容** | 一个线程迁移一部分，别的线程帮扛 |

### put 流程核心

```
① 计算 hash → spread(key.hashCode())
② 桶为空 → CAS 插入新 Node，成功就结束
③ 遇到 ForwardingNode（hash=-1）→ 协助扩容
④ 桶不为空 → synchronized(f) 锁头节点，遍历链表/红黑树
    ├ 找到相同 key → 覆盖 value
    └ 没找到 → 尾插法（链表）或红黑树插入
⑤ 链表长度 > 8 且数组 ≥ 64 → 转红黑树
⑥ addCount → 检查是否需要扩容
```

### get 流程

**基本不加锁**，依赖 volatile 保证可见性：
- Node 的 `val` 和 `next` 都是 `volatile` 修饰
- 一个线程修改后，其他线程 get 能立刻看到

### 为什么 JDK 1.8 用 synchronized 而不是 ReentrantLock？

因为 JDK 1.6 之后 JVM 对 synchronized 做了大量优化（锁升级：偏向锁→轻量级锁→重量级锁），性能已经不输 ReentrantLock，而且：
- synchronized 自动释放锁，不会忘写 unlock
- JVM 层面优化，比 ReentrantLock 的对象更轻量
- 代码更简洁

---

## 1.7 vs 1.8 总对比

| 维度 | JDK 1.7 | JDK 1.8 |
|------|---------|---------|
| **数据机构** | Segment 数组 + HashEntry 链表 | Node 数组 + 链表 + 红黑树 |
| **锁机制** | ReentrantLock（分段锁） | CAS + synchronized（桶级别） |
| **锁粒度** | 一个 Segment（包含多个桶） | 一个桶（链表/红黑树头节点） |
| **并发度** | 固定 16（Segment 数量） | 理论等于数组长度 |
| **扩容** | 单 Segment 扩容 | 多线程协同扩容 |
| **get** | 无锁（volatile） | 无锁（volatile） |
| **遇到扩容** | 等锁 | ForwardingNode + helpTransfer 协助 |
| **size 统计** | 分段计数 | baseCount + CounterCell |

---

## 面试高频追问

### Q1: ConcurrentHashMap 如何保证 get 不用加锁？

答：Node 的 `val` 和 `next` 都用 `volatile` 修饰，保证了可见性。写线程修改了 val 后，读线程立刻能看到最新值，不需要加锁。

### Q2: 为什么 ConcurrentHashMap 不允许 null 键和 null 值？

答：如果 get(key) 返回 null，你无法判断是 key 不存在还是 value 就是 null。HashMap 可以这样做是因为它是单线程的，但并发环境下做这种区分有歧义。

### Q3: size() 是怎么统计元素数量的？

答：先用 baseCount 累加，如果 CAS 竞争激烈（baseCount 频繁失败），就创建 CounterCell 数组，每个线程往自己的 Cell 里加。最后求和 baseCount + 所有 CounterCell 的值。这叫**分段计数**，分散了并发压力。

### Q4: 头插法导致的死循环在 ConcurrentHashMap 中存在吗？

答：不存在。1.7 的 ConcurrentHashMap 本身就加了锁，不会出现多线程同时扩容的情况。1.8 更没问题——没了头插法，还有锁保护。
