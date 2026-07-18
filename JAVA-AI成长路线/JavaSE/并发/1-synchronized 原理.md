# synchronized 原理

---

## 核心

synchronized 是 Java 内置的锁机制，保证同一时刻只有一个线程执行被保护的代码块。

---

## 用法

```java
// 修饰实例方法——锁当前对象
public synchronized void method() {
    // 同一时刻只有一个线程能执行此方法
}

// 修饰静态方法——锁当前类的 Class 对象
public static synchronized void staticMethod() {
    // 锁定的是整个类
}

// 同步代码块——锁任意对象
public void method() {
    synchronized (this) {
        // 精确控制锁的范围
    }
}
```

---

## 关键理解

**本质**：synchronized 基于 Java 对象头的 Mark Word 实现。JDK 6 之后引入了锁升级机制来优化性能：

```
无锁 → 偏向锁 → 轻量级锁（自旋） → 重量级锁（OS 互斥量）
```

| 锁状态 | 场景 | 开销 |
|--------|------|------|
| 无锁 | 没有线程竞争 | 无 |
| 偏向锁 | 只有一个线程反复获取 | 极低 |
| 轻量级锁 | 少量线程交替执行，短时间自旋等待 | 较低 |
| 重量级锁 | 多线程激烈竞争，线程阻塞等待 | 高 |

锁可以升级，不能降级。

---

## 实际使用

```java
public class Counter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;  // 多线程下安全递增
    }
    
    public synchronized int getCount() {
        return count;
    }
}
```

---

## vibe coding 视角

- AI 生成的同步代码通常会直接使用 synchronized，这是合理的选择
- 判断 synchronized 的使用范围是否恰当——锁的粒度尽量小，只包裹需要保护的代码
- 注意区分锁的是对象还是类，这决定了锁的范围
- Lock 的高级特性（可中断、尝试获取）不常用，遇到时知道有另一种机制即可

---

## 关联知识点

- [[并发/6-多线程基础]] — synchronized 解决多线程竞争共享资源的问题
- [[并发/5-Lock]] — Lock 是 synchronized 之外的另一种锁机制，提供更灵活的控制
- [[集合/2-ConcurrentHashMap]] — ConcurrentHashMap 内部使用 synchronized 锁头节点

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **库存扣减** | 黑马点评秒杀场景，synchronized 保证库存不超卖 |
| **计数统计** | 高并发下累计访问次数等统计操作 |
| **缓存更新** | 缓存失效后回源数据库时，防止大量请求同时打到数据库 |
