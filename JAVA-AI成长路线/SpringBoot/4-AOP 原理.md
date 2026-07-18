# AOP 原理

---

## 核心

AOP（面向切面编程）允许在不修改原有代码的情况下，在方法执行前后插入通用逻辑——`@Transactional`、`@Async` 都是基于 AOP 实现的。

---

## 为什么需要 AOP

```java
// ❌ 没有 AOP：每个方法都要写重复代码
public class OrderService {
    public void createOrder(OrderDTO dto) {
        long start = System.currentTimeMillis();
        try {
            // 业务逻辑
            orderMapper.insert(dto);
        } finally {
            log.info("耗时：{}ms", System.currentTimeMillis() - start);
        }
    }
    
    public void cancelOrder(Long id) {
        long start = System.currentTimeMillis();
        try {
            // 业务逻辑
            orderMapper.updateStatus(id, "cancelled");
        } finally {
            log.info("耗时：{}ms", System.currentTimeMillis() - start);
        }
    }
    // 每个方法都要写同样的耗时统计
}

// ✅ 用 AOP：写一次，到处生效
@Aspect
@Component
public class TimeCostAspect {
    @Around("@annotation(annotation.Trace)")
    public Object measure(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();  // 执行目标方法
        log.info("{} 耗时：{}ms", pjp.getSignature().getName(), 
                 System.currentTimeMillis() - start);
        return result;
    }
}
```

---

## 核心概念

| 概念 | 含义 | 类比 |
|------|------|------|
| **Aspect（切面）** | 横切关注点的集合（日志、事务等） | 一个切面 = 一个通用功能 |
| **JoinPoint（连接点）** | 可以被拦截的方法 | 所有方法都是潜在连接点 |
| **Pointcut（切点）** | 具体要拦截哪些方法 | 定义"在哪里插代码" |
| **Advice（通知）** | 拦截后执行的逻辑 | 定义"插入什么代码" |
| **Weaving（织入）** | 把切面应用到目标对象的过程 | 实际插入代码的动作 |

---

## 5 种通知（Advice）

```java
@Before("pointcut()")          // 方法执行前
public void before() { ... }

@After("pointcut()")           // 方法执行后（不管是否异常）
public void after() { ... }

@AfterReturning("pointcut()")  // 方法正常返回后
public void afterReturning() { ... }

@AfterThrowing("pointcut()")   // 方法抛出异常后
public void afterThrowing() { ... }

@Around("pointcut()")          // 包裹整个方法（最常用）
public Object around(ProceedingJoinPoint pjp) {
    // 方法执行前
    Object result = pjp.proceed();  // 执行目标方法
    // 方法执行后
    return result;
}
```

`@Around` 是最灵活的一种，可以实现前四种的所有功能。

---

## 底层实现

Spring AOP 通过**动态代理**实现：

```java
// 目标类有接口 → JDK 动态代理
public interface UserService { ... }
@Service
public class UserServiceImpl implements UserService { ... }
// Spring 生成一个实现了 UserService 接口的代理对象

// 目标类没有接口 → CGLIB 代理
@Service
public class UserService { ... }
// Spring 生成一个 UserService 的子类作为代理对象
```

```
调用方 → 代理对象（AOP 插入逻辑）→ 原始 Bean 的方法
              ↑
        这里做了事务开启、日志记录等
```

---

## @Transactional 的 AOP 实现

```java
@Transactional
public void createOrder(OrderDTO dto) {
    orderMapper.insert(dto);
    accountMapper.deduct(dto.getUserId(), dto.getAmount());
}
```

Spring 通过 AOP 在 `createOrder` 前后插入事务逻辑：

```
代理对象.createOrder() {
    try {
        beginTransaction();           // @Before：开启事务
        target.createOrder(dto);      // 实际方法
        commitTransaction();          // @AfterReturning：提交事务
    } catch (Exception e) {
        rollbackTransaction();        // @AfterThrowing：回滚事务
    }
}
```

**重要推论**：同一个类中方法直接调用（A 方法调用 B 方法），不会走代理对象，`@Transactional` 不会生效。

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **@Transactional** | 项目中最常用的 AOP 应用——方法执行前后自动管理事务 |
| **耗时统计** | 可以用 AOP 统一记录所有 API 的响应时间 |
| **权限校验** | AOP 在方法级别校验当前用户是否有权限执行此操作 |
| **日志记录** | 记录方法入参、返回值、异常信息 |
