# @Autowired 与依赖注入

---

## 核心

`@Autowired` 告诉 Spring 把需要的 Bean 注入进来。默认按类型匹配，同类型有多个时按名称匹配。

---

## @Autowired 默认按类型注入

```java
@Service
public class OrderService {
    @Autowired
    private UserService userService;  // Spring 找 UserService 类型的 Bean 注入
}
```

只有一个 `UserService` 的实现时，没有任何歧义。

---

## 同类型多个 Bean 时的处理

```java
// 多个实现
public interface PaymentService {
    void pay(BigDecimal amount);
}

@Service
public class AlipayService implements PaymentService { ... }

@Service
public class WechatPayService implements PaymentService { ... }
```

此时 `@Autowired` 按类型找不到唯一 Bean，需要用以下方式指定：

```java
// 方式一：@Qualifier 指定名称（Bean 默认名称是类名首字母小写）
@Autowired
@Qualifier("alipayService")
private PaymentService paymentService;

// 方式二：@Resource 按名称注入（Java 的注解，不是 Spring 的）
@Resource(name = "alipayService")
private PaymentService paymentService;

// 方式三：收集所有同类型 Bean（注入一个列表）
@Autowired
private List<PaymentService> paymentServices;  // 拿到所有 PaymentService 实现
```

---

## @Autowired vs @Resource

| | @Autowired | @Resource |
|--|-----------|-----------|
| 来源 | Spring | Java（javax.annotation） |
| 默认匹配方式 | byType（按类型） | byName（按名称） |
| 指定名称 | `@Qualifier` | `name` 属性 |
| 多个同类型 Bean | 必须指定 Qualifier | 名称匹配到唯一则直接注入 |

**实际使用**：大部分场景用 `@Autowired` 就够了。需要按名称注入时也可以直接用 `@Resource`。

---

## @Autowired 的可选依赖

```java
@Autowired(required = false)     // 如果找不到对应的 Bean，注入 null
private EmailService emailService;  // 有就注入，没有也不影响启动

// 如果没有 @Autowired(required = false)，找不到 Bean 启动直接报错
@Autowired                         // 容器中没有 EmailService → 启动失败
private EmailService emailService;
```

---

## @Primary——指定首选 Bean

```java
@Service
@Primary                           // 当有多个同类型 Bean 时，优先注入这个
public class DefaultPaymentService implements PaymentService { ... }

// 其他地方直接 @Autowired，不需要 Qualifier
@Autowired
private PaymentService paymentService;  // 拿到的是 DefaultPaymentService
```

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **Service 注入 Mapper** | `@Autowired private UserMapper userMapper;` — 最常见的用法 |
| **多种 AI 模型实现** | 如果有多个 LLM 实现（GPT、Claude），可用 `@Qualifier` 指定 |
| **配置类注入** | `@Configuration` 类中的 `@Bean` 方法通过参数注入其他 Bean |
