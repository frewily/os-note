# == 与 equals

---

## 核心

`==` 比较内存地址，`equals` 比较对象内容（可重写）。

---

## == 运算符

**行为**：
- 基本类型：比较值是否相等
- 引用类型：比较内存地址（是否是同一个对象）

```java
int a = 1, b = 1;
a == b;  // true，基本类型比值

String s1 = "hello";
String s2 = "hello";
s1 == s2;  // true，字符串常量池复用同一个对象

String s3 = new String("hello");
s1 == s3;  // false，new 强制创建了新对象
```

---

## equals 方法

**行为**：`Object` 的默认实现等同于 `==`，但可被子类重写为按内容比较。

```java
// Object 默认实现
public boolean equals(Object obj) {
    return (this == obj);  // 就是比地址
}

// String 重写后
String a = "hello";
String b = new String("hello");
a.equals(b);  // true，String 重写了 equals，按字符数组内容比较
```

**重写 equals 的通用模式**：

```java
public class User {
    private String name;
    private int age;
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return age == user.age && Objects.equals(name, user.name);
    }
}
```

---

## 关键场景：String 比较

```java
String s1 = "hello";               // 常量池
String s2 = "hello";               // 复用常量池对象
String s3 = new String("hello");   // 堆上新对象

s1 == s2      // true
s1 == s3      // false
s1.equals(s3) // true
```

**原则**：比较字符串内容始终用 `equals`，不用 `==`。

---

## vibe coding 视角

AI 生成的代码中，`==` 和 `equals` 的用法通常正确。阅读代码时关注两点：

1. 自定义对象在 Set 中或作为 HashMap key 使用时，是否重写了 `equals` 和 `hashCode`
2. 字符串比较是否用了 `equals` 而非 `==`

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **JWT 用户信息比较** | Token 解析出的用户对象做相等判断，依赖 equals |
| **HashSet 去重** | 底层调用 `hashCode()` + `equals()`，自定义对象不重写则去重失效 |
| **Redis key 比较** | 字符串 key 的比较统一用 equals |
