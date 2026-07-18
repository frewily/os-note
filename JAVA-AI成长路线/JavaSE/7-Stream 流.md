# Stream 流

---

## 核心

Stream 是 Java 8 引入的数据处理方式，用声明式的链条操作代替手写 for 循环——过滤、转换、收集一气呵成。

---

## 基础：Lambda 表达式

Stream 离不开 Lambda，先看懂 Lambda 就够了：

```java
// 传统写法
list.sort(new Comparator<User>() {
    public int compare(User a, User b) {
        return a.getAge() - b.getAge();
    }
});

// Lambda 写法
list.sort((a, b) -> a.getAge() - b.getAge());

// 更精简：方法引用
list.sort(Comparator.comparingInt(User::getAge));
```

**读法**：`->` 箭头左边是参数，右边是逻辑。`::` 是直接引用一个方法。

---

## Stream 三板斧

Stream 操作分三段：**创建 → 中间操作（可链式） → 终止操作**

```java
list.stream()           // ① 创建流
    .filter(...)         // ② 中间操作（可多个）
    .map(...)
    .collect(...);       // ③ 终止操作（执行后流关闭）
```

### 常用操作

```java
List<User> users = getUserList();

// filter — 筛选
users.stream()
    .filter(u -> u.getAge() > 18)
    .collect(Collectors.toList());

// map — 转换（从 A 变成 B）
users.stream()
    .map(User::getName)
    .collect(Collectors.toList());  // 得到 List<String>

// forEach — 遍历（不收集结果）
users.stream()
    .filter(u -> u.getAge() > 18)
    .forEach(u -> System.out.println(u.getName()));

// collect — 收集为各种集合
users.stream().collect(Collectors.toList());       // List
users.stream().collect(Collectors.toSet());        // Set
users.stream().collect(Collectors.toMap(           // Map
    User::getId,     // key
    u -> u           // value
));

// sorted — 排序
users.stream()
    .sorted(Comparator.comparingInt(User::getAge))
    .collect(Collectors.toList());

// count — 计数
long count = users.stream()
    .filter(u -> u.getAge() > 18)
    .count();
```

---

## Optional — 优雅处理空值

```java
// 传统：大量 if-null 判断
public String getUserName(User user) {
    if (user != null) {
        Address addr = user.getAddress();
        if (addr != null) {
            return addr.getCity();
        }
    }
    return "未知";
}

// Optional：流水线式处理
public String getUserName(User user) {
    return Optional.ofNullable(user)
        .map(User::getAddress)
        .map(Address::getCity)
        .orElse("未知");
}
```

**核心方法**：

| 方法 | 作用 |
|------|------|
| `ofNullable(obj)` | 包装可能为 null 的对象 |
| `map()` | 对象不为 null 时执行转换 |
| `orElse(default)` | 为 null 时返回默认值 |
| `orElseGet(() -> {})` | 为 null 时执行逻辑获取默认值 |
| `orElseThrow(() -> {})` | 为 null 时抛异常 |
| `ifPresent(v -> {})` | 不为 null 时执行操作 |

---

## 进阶但常用的技巧

```java
// 分组
Map<Integer, List<User>> groupByAge = 
    users.stream().collect(Collectors.groupingBy(User::getAge));

// 去重（根据某个字段）
List<User> distinctByName = 
    users.stream()
        .filter(distinctByKey(User::getName))
        .collect(Collectors.toList());

// 提取指定字段的列表
List<Long> ids = 
    users.stream().map(User::getId).collect(Collectors.toList());
```

---

## vibe coding 视角

- Stream 是 AI 在处理集合时的**默认风格**，理解 pipeline 模式（创建→过滤/转换→收集）即可流畅阅读
- 不必记忆所有 Collector 方法，常用的记 `.collect(Collectors.toList())`，其余需要时查文档
- Optional 主要用来处理链式调用中的空值，避免大量 if-null
- **什么时候不用 Stream**：逻辑复杂（超过 3 个操作）、需要异常处理（try-catch 包裹不了 Lambda 内部）、需要 break/continue

---

## 关联知识点

- [[index]] — 返回知识地图
- [[6-泛型]] — Stream 的方法签名（如 `Stream<T>`）依靠泛型实现类型安全

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **列表过滤** | 从用户列表筛选出有权限的用户 |
| **DTO 转换** | Entity → VO/DTO 的批量转换 |
| **分组统计** | 按订单状态分组统计数量 |
| **ID 提取** | 从对象列表提取 ID 列表传给下一个接口 |
| **空值安全获取** | 链式获取嵌套对象的属性（用户 → 地址 → 城市） |
