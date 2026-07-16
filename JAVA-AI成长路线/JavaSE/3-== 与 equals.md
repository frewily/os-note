# == 与 equals

---

## 一句话核心

`==` 比的是"是不是同一个东西"，`equals` 比的是"内容是不是一样"——AI 写代码时基本不会在这出错，但你读代码时得知道它在比什么。

---

## 为什么用

最常见翻车场景：**用 `==` 比较字符串**。

```java
String a = "hello";
String b = new String("hello");
System.out.println(a == b);      // false — 不是同一个对象
System.out.println(a.equals(b)); // true — 内容一样
```

这种 bug AI 很少犯，但**你 review AI 生成的代码时**，如果看到 `==` 在比较对象（尤其是 String），你要能意识到"这里是不是应该用 equals？"

另一个场景：AI 生成的代码里，自定义的类用了 `equals`，但你没重写过——结果永远 false。你要知道问题出在哪。

---

## 关键理解

### 基本类型

```java
int a = 1;
int b = 1;
a == b  // true，基本类型 == 直接比值
```

基本类型没有 `equals` 方法，只能用 `==`。

### 引用类型

```java
User u1 = new User("张三");
User u2 = new User("张三");
u1 == u2       // false — 两个对象在堆里不同位置
u1.equals(u2)  // false — Object 默认 equals 也是比地址
```

`Object` 的默认 `equals` 就是用 `==`，所以如果你不重写，equals 和 == 没区别。

### String 的特殊之处

```java
String s1 = "hello";              // 放到字符串常量池
String s2 = "hello";              // 从常量池拿，和 s1 是同一个对象
String s3 = new String("hello");  // 强制 new，新对象

s1 == s2   // true（常量池复用）
s1 == s3   // false（新对象）
s1.equals(s3)  // true（内容一样）
```

这就是为什么**永远用 equals 比字符串**——你不用去猜它是不是常量池里的。

---

## 代码看一眼

```java
// 自定义类重写 equals 的通用写法
public class User {
    private String name;
    private int age;
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;           // 同一个对象 → 肯定相等
        if (o == null || getClass() != o.getClass()) return false;  // 类型不同
        User user = (User) o;
        return age == user.age && 
               Objects.equals(name, user.name);  // 比较关键字段
    }
}

// 实际使用时
User u1 = new User("张三", 18);
User u2 = new User("张三", 18);
u1.equals(u2);  // true，因为重写了 equals
```

---

## 你的项目里

| 场景 | 说明 |
|------|------|
| **JWT 校验** | token 解析出来的用户信息做比较，用 `equals` 而不是 `==` |
| **缓存 key 比较** | Redis 的 key 通常是字符串，比较时用 `equals` |
| **Set/HashMap 去重** | HashSet 判断元素是否重复，底层调的就是 `hashCode()` + `equals()`。如果往 Set 里放自定义对象没有重写 equals，去重会失效 |
