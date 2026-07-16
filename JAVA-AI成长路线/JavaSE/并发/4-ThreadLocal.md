# ThreadLocal

---

## 核心

ThreadLocal 为每个线程维护一份独立的变量副本，线程之间互不干扰。

---

## 为什么需要

Web 服务器使用线程池处理请求，一个请求的处理过程中，需要在多个方法之间传递同一个数据（如当前登录用户）。如果将数据作为参数层层传递，代码会非常冗余。

ThreadLocal 让线程拥有自己的私有存储，在链路的任意位置存取数据。

---

## 用法

```java
// 定义
private static final ThreadLocal<Long> USER_ID_HOLDER = new ThreadLocal<>();

// 存——在拦截器中存入
USER_ID_HOLDER.set(userId);

// 取——在 Service 层任意位置取
Long currentUserId = USER_ID_HOLDER.get();

// 删——请求结束后必须清理
USER_ID_HOLDER.remove();
```

## 典型链路

```
请求 → 拦截器（解析 JWT，userId 存入 ThreadLocal）
         → Controller（从 ThreadLocal 取 userId）
              → Service（从 ThreadLocal 取 userId）
                   → Dao

请求结束 → 拦截器（ThreadLocal.remove() 清理）
```

---

## 内存泄漏问题

**原因**：ThreadLocal 的 key 是弱引用，value 是强引用。ThreadLocal 对象被回收后，key 变为 null，但 value 仍然存在，无法被访问也无法被回收。

**解决方案**：使用完后必须调用 `remove()` 清理。

```java
try {
    USER_ID_HOLDER.set(userId);
    // 业务逻辑
} finally {
    USER_ID_HOLDER.remove();  // 确保一定执行清理
}
```

在 Web 环境下尤为重要——线程池会复用线程，不清理可能导致不同请求读到同一个 ThreadLocal 中残留的数据。

---

## vibe coding 视角

- ThreadLocal 在 Web 项目中主要用于传递当前用户信息、请求追踪 ID
- AI 生成的代码中，ThreadLocal 出现时重点检查是否在 finally 块中调用了 remove
- 不清理 < 不设置——漏掉 remove 的影响比漏掉 set 更大

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **当前用户信息** | 拦截器解析 JWT 后存入 ThreadLocal，后续链路直接取用 |
| **请求追踪 ID** | 每个请求分配唯一 ID，存入 ThreadLocal 用于日志关联 |
| **分布式链路追踪** | 追踪 ID 在微服务间传递时，ThreadLocal 是常用的载体 |
