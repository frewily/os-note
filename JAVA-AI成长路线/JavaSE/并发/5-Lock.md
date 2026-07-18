# Lock

---

## 核心

Lock 是 synchronized 之外的另一种锁机制，提供更灵活的控制——可中断、可超时、可尝试获取。

---

## synchronized vs Lock

| | synchronized | Lock |
|--|------------|------|
| 使用方式 | 关键字，隐式加解锁 | API，需要手动 lock/unlock |
| 自动释放 | 是（退出作用域自动释放） | 否（必须 finally 中 unlock） |
| 可中断 | 否（等待锁时不可中断） | 是（lockInterruptibly） |
| 超时获取 | 否 | 是（tryLock(3s)） |
| 公平性 | 非公平 | 可指定公平或非公平 |

---

## 基本用法

```java
private final Lock lock = new ReentrantLock();

public void doSomething() {
    lock.lock();
    try {
        // 被保护的代码
    } finally {
        lock.unlock();  // 必须手动释放
    }
}
```

## 高级特性

```java
// 尝试获取锁，获取不到就做其他事
if (lock.tryLock()) {
    try {
        // 获取成功
    } finally {
        lock.unlock();
    }
} else {
    // 获取失败，执行兜底逻辑
}

// 尝试获取锁，最多等 3 秒
if (lock.tryLock(3, TimeUnit.SECONDS)) {
    // 3 秒内获取成功
}

// 可中断的锁等待
lock.lockInterruptibly();  // 其他线程可以中断当前线程的等待
```

---

## 选择建议

- **优先使用 synchronized**：写法简单，自动释放锁，不会因为忘记 unlock 导致死锁
- **使用 Lock 的场景**：需要尝试获取锁（`tryLock`）、需要等待超时、需要可中断等待
- **ReentrantLock 默认非公平**，性能更好但可能导致线程饥饿

---

## vibe coding 视角

- AI 生成的代码中使用 synchronized 还是 Lock，取决于具体场景
- 如果看到 Lock，检查是否在 finally 中 unlock——这是最常见的错误
- 优先推荐 synchronized，除非确实需要 Lock 的高级特性

---

## 关联知识点

- [[并发/1-synchronized 原理]] — Lock 和 synchronized 解决相同问题，用法不同
- [[并发/6-多线程基础]] — Lock 用于复杂的多线程同步场景

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **缓存互斥** | 缓存失效时，尝试加锁回源数据库，获取不到锁的线程直接返回旧值（避免等待） |
| **定时任务互斥** | 集群环境下，多个节点同时执行定时任务时用分布式锁（Redis），单机场景可用 Lock |
