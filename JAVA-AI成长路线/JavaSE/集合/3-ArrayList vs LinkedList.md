# ArrayList vs LinkedList

---

## 核心

ArrayList 用数组实现，随机访问快；LinkedList 用双向链表实现，头尾增删快。

---

## 对比

| 维度 | ArrayList | LinkedList |
|------|-----------|------------|
| 底层结构 | 动态数组 | 双向链表 |
| 随机访问 | O(1) — 直接索引 | O(n) — 需遍历 |
| 尾部插入 | O(1) 均摊 | O(1) |
| 头部/中间插入 | O(n) — 需位移元素 | O(1) 头部 / O(n) 遍历到位置 |
| 内存占用 | 更紧凑 | 更大（每个节点存前后指针） |
| 扩容策略 | 1.5 倍扩容 | 不需要扩容 |

```java
// ArrayList：连续内存，下标直接访问
List<String> arrayList = new ArrayList<>();
arrayList.add("a");     // 追加到末尾 O(1)
arrayList.get(5);       // 直接通过下标获取 O(1)
arrayList.add(0, "x");  // 插入头部，后续元素全部后移 O(n)

// LinkedList：节点分散，通过指针连接
List<String> linkedList = new LinkedList<>();
linkedList.add("a");        // 追加到末尾 O(1)
linkedList.addFirst("x");   // 插入头部 O(1)
linkedList.get(5);          // 从头遍历到第 5 个 O(n)
```

---

## 选择依据

| 场景 | 选用 |
|------|------|
| 频繁随机访问（按索引取值） | ArrayList |
| 主要是追加操作，很少插入/删除 | ArrayList |
| 频繁头部插入或删除 | LinkedList |
| 需要实现队列/双端队列 | LinkedList（实现了 Deque 接口） |

**vibe coding 视角**：90% 的场景默认用 ArrayList。只有明确需要频繁头部操作时才用 LinkedList。AI 通常默认生成 ArrayList，这是合理的选择。

---

## 项目关联

| 场景 | 选用 | 原因 |
|------|------|------|
| 从数据库查询返回多条记录 | ArrayList | 只需遍历，不涉及头部插入 |
| 缓存最新消息列表 | LinkedList | 频繁在头部插入新消息 |
| API 返回 List 数据 | ArrayList | 前端大概率要遍历，不需要随机访问特殊优化 |
