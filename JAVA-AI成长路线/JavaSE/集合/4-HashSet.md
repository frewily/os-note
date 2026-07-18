# HashSet

---

## 核心

HashSet 底层是 HashMap，元素作为 HashMap 的 key 存储，利用 key 不可重复的特性保证元素唯一性。

---

## 原理

```java
// HashSet 源码核心
public class HashSet<E> {
    private transient HashMap<E, Object> map;
    private static final Object PRESENT = new Object();  // 固定的占位 value
    
    public boolean add(E e) {
        return map.put(e, PRESENT) == null;  // 元素作为 key 存入 HashMap
    }
    
    public boolean contains(Object o) {
        return map.containsKey(o);
    }
}
```

- 存入 Set 的元素作为 HashMap 的 **key**
- 所有 key 共享同一个占位 value（`PRESENT`）
- 利用 HashMap key 不能重复的特性保证元素不重复

---

## 核心要求

放入 HashSet 的元素必须正确重写 `hashCode()` 和 `equals()`：

```java
public class User {
    private Long id;
    private String name;
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return Objects.equals(id, user.id);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id);  // 与 equals 保持一致的字段
    }
}

// 现在 HashSet 可以用 User 对象去重
Set<User> userSet = new HashSet<>();
userSet.add(new User(1L, "张三"));
userSet.add(new User(1L, "张三"));  // 不会重复添加
```

如果 `hashCode()` 没有重写，默认继承 Object 的实现（基于内存地址），即使内容相同的两个对象也会被认为是不同元素。

---

## 常用操作

```java
Set<String> set = new HashSet<>();
set.add("apple");
set.add("banana");
set.add("apple");       // 不会重复
set.contains("apple");  // true
set.size();             // 2
set.remove("apple");
```

**注意**：HashSet 不保证元素的顺序。需要有序时可使用 `LinkedHashSet`（插入顺序）或 `TreeSet`（排序）。

---

## vibe coding 视角

- AI 生成去重逻辑时通常会使用 HashSet，理解其依赖 hashCode + equals 即可
- 自定义对象放入 HashSet 后去重失效，问题大概率出在未重写 hashCode/equals
- 不需要记忆 HashSet 内部 HashMap 的初始容量、负载因子等参数

---

## 关联知识点

- [[../JavaSE]] — 返回知识地图
- [[集合/1-HashMap]] — HashSet 底层直接使用 HashMap，元素作为 key 存储

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **权限去重** | 用户拥有多个角色，角色有重复权限，用 Set 存储权限标识自动去重 |
| **已处理 ID 记录** | 批量处理任务时，已处理的任务 ID 存入 Set 防止重复消费 |
| **标签去重** | 用户标签或兴趣标签去重存储 |
