# Bean 生命周期

---

## 核心

Spring 管理从 Bean 创建到销毁的全过程——实例化 → 属性赋值 → 初始化 → 使用 → 销毁。

---

## 完整流程

```
① 实例化       → Spring 通过反射创建对象（调用构造器）
② 属性赋值      → 注入 @Autowired 等依赖
③ 初始化前      → @PostConstruct 方法执行
④ 初始化        → InitializingBean.afterPropertiesSet() 或 @Bean(initMethod = "")
⑤ 初始化后      → AOP 代理在此生成（如果有 @Transactional 等注解）
⑥ 使用 Bean     → 项目运行中调用
⑦ 销毁          → @PreDestroy 或 DisposableBean.destroy()
```

---

## 代码演示

```java
@Component
public class UserService {
    
    public UserService() {
        System.out.println("① 实例化：构造器执行");
    }
    
    @Autowired
    private UserMapper userMapper;  // ② 属性赋值
    
    @PostConstruct
    public void init() {
        System.out.println("③ 初始化前：@PostConstruct 执行");
        // 适合在这里做初始化检查、缓存预热等
    }
    
    // ④ 初始化方法（如果实现了 InitializingBean）
    @Override
    public void afterPropertiesSet() {
        System.out.println("④ 初始化：afterPropertiesSet 执行");
    }
    
    // 业务方法——⑤ 初始化后生成 AOP 代理，⑥ 使用 Bean
    
    @PreDestroy
    public void destroy() {
        System.out.println("⑦ 销毁：@PreDestroy 执行");
        // 释放资源、关闭连接等
    }
}
```

---

## 各阶段的实际用途

| 阶段 | 可以做 | 不要做 |
|------|--------|--------|
| 构造器 | 简单的字段初始化 | 调用依赖的对象（还没注入） |
| @PostConstruct | 缓存预热、数据校验、启动检查 | 耗时太长的操作 |
| 使用 | 业务逻辑 | — |
| @PreDestroy | 释放资源、关闭线程池 | 复杂的清理逻辑 |

---

## AOP 代理的生成时机

**在第⑤步（初始化后）**，Spring 检查 Bean 上是否有 `@Transactional`、`@Async` 等注解。如果有，通过动态代理生成代理对象，替代原来的 Bean。

```
原始 Bean（UserService）→ 检测到 @Transactional → 生成代理对象
                                                      ↓
                                              代理对象包裹原始 Bean
                                              方法调用前后加事务逻辑
```

所以 `@PostConstruct` 是在**原始 Bean 上执行**的，此时 AOP 还没有生成。在 `@PostConstruct` 中调用本类加了 `@Transactional` 的方法，事务不会生效。

---

## 项目关联

| 阶段 | 在项目中的体现 |
|------|---------------|
| **@PostConstruct** | 项目启动时加载配置、初始化缓存、检查数据库连接 |
| **初始化后 + AOP** | `@Transactional` 方法在此时才真正具备事务能力 |
| **销毁** | 应用关闭前释放线程池、断开数据库连接 |
