# volatile 关键字

---

## 核心

volatile 保证变量的可见性，并禁止指令重排序。

---

## 两个作用

### 1. 可见性

一个线程修改 volatile 变量后，其他线程立即可见。

```java
public class Flag {
    private volatile boolean running = true;
    
    public void stop() {
        running = false;  // 修改后，其他线程立刻看到
    }
    
    public void work() {
        while (running) {  // 不加 volatile，这里可能永远读不到新值
            // 循环工作
        }
    }
}
```

不加 volatile 时，线程可能一直读取 CPU 缓存中的旧值，看不到其他线程的修改。

### 2. 禁止指令重排序

编译器和 CPU 可能会为了优化而改变指令执行顺序。volatile 在读写前后插入内存屏障，防止重排序。

**典型场景**：单例模式的双重检查锁定。

```java
private volatile static Singleton instance;
```

不加 volatile 时，`instance = new Singleton()` 的指令可能被重排序，导致其他线程拿到未初始化完成的对象。

---

## volatile 不保证原子性

```java
private volatile int count = 0;
count++;  // 不是原子操作！→ 读取 + 加一 + 写入，三步可能被打断
```

需要原子性时应使用 `AtomicInteger`、`synchronized` 或 `Lock`。

---

## synchronized vs volatile

| | synchronized | volatile |
|--|------------|----------|
| 可见性 | 保证 | 保证 |
| 原子性 | 保证 | 不保证 |
| 性能 | 较高（涉及锁） | 极低（无锁） |
| 适用 | 复合操作 | 单一变量状态标志 |

---

## vibe coding 视角

- volatile 在 AI 生成的代码中主要出现在状态标志位（如 `running`、`shutdown`）和单例模式中
- 理解"可见性"的含义即可——volatile 解决的是"线程看不到另一个线程改了什么"的问题
- 看到 volatile 修饰的变量在做复合操作（如 `count++`），应意识到原子性问题

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **服务开关** | 动态控制服务是否接受新请求，一个线程修改标志，工作线程立刻感知 |
| **缓存刷新标志** | 定时刷新缓存的开关，通知工作线程重新加载 |
