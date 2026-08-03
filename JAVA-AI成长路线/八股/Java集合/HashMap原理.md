---
publish: true
---

# HashMap 原理（参考资源整理）

> 来源：CSDN / JavaGuide / 掘金 多篇文章综合整理

---

## 关联知识点

- [[八股/八股笔记]] — 八股笔记汇总
> 整理时间：2026-05-14

---

## 一、底层数据结构

- **JDK 1.7**：数组（`Entry[]`） + 单向链表
- **JDK 1.8**：数组（`Node[]`） + 单向链表 + 红黑树

```
数组（table）
 ┌───┬───┬───┬───┬───┐
 │ 0 │ 1 │ 2 │ 3 │…  │
 └─┬─┴───┴─┬─┴───┴───┘
   ↓       ↓
  链表   红黑树
```

核心节点结构：
- `Node`：hash、key、value、next（链表节点）
- `TreeNode`（继承自 LinkedHashMap.Entry）：parent、left、right、prev、red（红黑树节点）

---

## 二、put 方法完整流程（JDK 1.8 重点）

当调用 `map.put(key, value)` 时，内部调用 `putVal(hash(key), key, value, false, true)`：

### 步骤 1：计算哈希值

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

- key 为 null → hash = 0（null 键存在数组第 0 位）
- 非 null → 高 16 位与低 16 位异或，称为「扰动函数」
- 目的：让高位参与低位运算，减少哈希冲突

> **JDK 1.7 vs 1.8**：1.7 做了 4 次位运算 + 5 次异或（9 次扰动），1.8 简化为 1 次异或。原因是 1.8 引入了红黑树，即使冲突也能保证 O(log n)，不再需要过度扰动。

### 步骤 2：定位桶位置

```java
i = (n - 1) & hash   // n 是数组长度（始终为 2 的幂）
```

- `&` 比 `%` 效率高（位运算 > 取模运算）
- 为什么数组长度必须是 2 的幂：保证 `n-1` 的二进制全为 1，这样 `hash & (n-1)` 等于 `hash % n`，且分布均匀

### 步骤 3：桶为空 → 直接插入

```java
if ((p = tab[i]) == null)
    tab[i] = newNode(hash, key, value, null);
```

### 步骤 4：桶不为空 → 处理哈希冲突

**4.1 判断桶的第一个节点**
```java
if (p.hash == hash && ((k = p.key) == key || key.equals(k)))
    e = p;  // key 相同，后续覆盖 value
```

**4.2 判断是否是红黑树节点**
```java
else if (p instanceof TreeNode)
    e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
```

**4.3 否则是链表 → 遍历**
```java
for (int binCount = 0; ; ++binCount) {
    if ((e = p.next) == null) {
        p.next = newNode(hash, key, value, null);  // 尾插法
        if (binCount >= TREEIFY_THRESHOLD - 1)  // 链表长度 >= 8
            treeifyBin(tab, hash);               // 转红黑树
        break;
    }
    if (e.hash == hash && key.equals(e.key))
        break;  // 找到相同 key
    p = e;
}
```

> **JDK 1.7 头插法 vs JDK 1.8 尾插法**：
> - 1.7：新节点插入链表头部 → 并发扩容时可能形成环形链表 → 死循环
> - 1.8：改为尾插法 → 避免死循环问题（但仍非线程安全，可能数据覆盖）

### 步骤 5：覆盖旧值

```java
if (e != null) {
    V oldValue = e.value;
    e.value = value;
    return oldValue;
}
```

### 步骤 6：检查是否需要扩容

```java
if (++size > threshold)  
    resize();
```

- `threshold = capacity × loadFactor`（默认 16 × 0.75 = 12）
- 当 size > threshold 时，扩容为原容量的 2 倍

---

## 三、扩容机制

### JDK 1.7 扩容
1. 创建新数组（2 倍）
2. 遍历旧数组所有节点
3. 每个节点重新计算 hash → 计算新下标
4. 头插法插入新数组
5. 问题：**链表顺序反转**，多线程可能死循环

### JDK 1.8 扩容优化

核心优化：**节点只可能落在两个位置：原位置 或 原位置 + oldCap**

因为数组长度翻倍（如 16 → 32），二进制多了一位。判断 `e.hash & oldCap` 的结果：
- 为 0 → 留在原位置
- 为 1 → 移动到 `原下标 + oldCap`

```
举例：oldCap=16（二进制 10000）
  hash 的第 5 位 = 0 → 位置不变
  hash 的第 5 位 = 1 → 位置 = 原位置 + 16
```

**优势**：不需要重新计算 hash，只有 O(1) 的位运算判断。

---

## 四、树化与反树化

| 条件 | 操作 |
|------|------|
| 链表长度 ≥ 8 **且** 数组长度 ≥ 64 | 链表 → 红黑树（treeifyBin） |
| 链表长度 ≥ 8 但数组长度 < 64 | 不转树，优先扩容（resize） |
| 红黑树节点数 ≤ 6 | 红黑树 → 链表（untreeify） |

**为什么阈值是 8？**

根据泊松分布，HashMap 负载因子为 0.75 时，链表长度达到 8 的概率约为 0.000006%（亿分之六），极少发生。这是一种「空间和时间」的权衡——树节点比链表节点占用更多内存，只在极低概率的极端情况下才转树。

---

## 五、HashMap 1.7 vs 1.8 对比总结

| 特性 | JDK 1.7 | JDK 1.8 |
|------|---------|---------|
| 数据结构 | 数组 + 单向链表 | 数组 + 单向链表 + **红黑树** |
| 插入方式 | 头插法 | 尾插法 |
| 哈希扰动 | 9 次位运算/异或 | 1 次异或 |
| 扩容节点迁移 | 重新计算 hash | 高位判断，只移动部分节点 |
| 链表转树 | 无 | 链表≥8 且 数组≥64 → 红黑树 |
| 扩容触发时机 | 先扩容再插入 | 先插入再扩容 |
| 并发问题 | **死循环**（环形链表）| 避免死循环，但仍会数据覆盖 |

---

## 六、关键常量

| 常量 | 值 | 含义 |
|------|----|------|
| DEFAULT_INITIAL_CAPACITY | 16（1 << 4） | 默认初始容量 |
| DEFAULT_LOAD_FACTOR | 0.75f | 默认负载因子 |
| TREEIFY_THRESHOLD | 8 | 链表 → 树阈值 |
| UNTREEIFY_THRESHOLD | 6 | 树 → 链表阈值 |
| MIN_TREEIFY_CAPACITY | 64 | 最小树化数组容量 |

---

## 七、线程安全问题

- **JDK 1.7**：并发扩容时头插法导致环形链表 → `get()` 时 CPU 100% 死循环
- **JDK 1.8**：即使尾插法避免了死循环，多线程 put 仍可能**数据覆盖**（丢失更新）
- **解决方案**：用 `ConcurrentHashMap` 替代 HashMap

---

## 八、面试回答模板（HashMap put 流程）

> 面试官：说说 HashMap 的 put 流程。

```
分 6 步：

1. 先对 key 做 hash 计算（高 16 位异或低 16 位），减少哈希冲突
2. 通过 (n-1) & hash 定位到数组中的 bucket 位置
3. 如果 bucket 为空，直接放入新节点
4. 如果不为空，说明发生哈希冲突：
   - 先判断第一个节点是不是相同 key（hash 相等且 equals），是就覆盖
   - 再判断是不是红黑树节点，是就按树的方式插入
   - 否则就是链表 → 遍历，尾插法追加；链表长度 ≥ 8 且数组 ≥ 64 时转红黑树
5. 如果找到相同 key，覆盖 value，返回旧值
6. 检查 size 是否 > threshold（容量 × 0.75），超过就扩容为 2 倍
```

---

## 九、面试追问清单（提前准备）

| 追问 | 答案要点 |
|------|---------|
| 为什么数组长度是 2 的幂？ | `(n-1) & hash` 代替取模；扩容时只移动部分节点 |
| 负载因子为什么是 0.75？ | 空间利用率 vs 冲突概率的折中。0.5 浪费空间，0.9 冲突严重 |
| 1.7 和 1.8 的区别？ | 红黑树 / 尾插法 / 简化扰动 / 扩容优化 |
| 为什么线程不安全？ | 1.7 死循环 + 1.8 数据覆盖 → 用 ConcurrentHashMap |
| 树化阈值为什么是 8？ | 泊松分布，概率极低（亿分之六），空间换时间 |
| HashSet 底层是什么？ | 就是 HashMap，元素作 key，固定常量作 value |
