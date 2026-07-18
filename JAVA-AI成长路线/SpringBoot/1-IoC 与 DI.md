# IoC 与 DI

---

## 核心

IoC（控制反转）把对象的创建权交给 Spring 容器，DI（依赖注入）是容器自动把依赖的对象注入进来——本质是同一件事的两个角度。

---

## 没有 IoC 的写法

```java
public class OrderService {
    private UserService userService = new UserService();    // 自己创建
    private EmailService emailService = new EmailService(); // 自己创建
    
    public void createOrder() {
        User user = userService.getCurrentUser();  // 强耦合
        emailService.send(user, "下单成功");         // 换实现要改代码
    }
}
```

问题：`OrderService` 和具体实现类**硬绑定**。想换 `UserService` 的实现（比如加缓存），需要改 `OrderService` 的代码。

---

## 有 IoC 的写法

```java
@Service                                    // 告诉 Spring：帮我管这个类
public class OrderService {
    
    @Autowired                              // 告诉 Spring：把 UserService 注入给我
    private UserService userService;
    
    @Autowired
    private EmailService emailService;
    
    public void createOrder() {
        User user = userService.getCurrentUser();
        emailService.send(user, "下单成功");
    }
}

// 如果需要换实现，加一个新实现类就行，OrderService 不用改
@Service
public class UserServiceCacheImpl extends UserService {
    // 带缓存的实现
}
```

**变化**：`OrderService` 不再自己 `new` 对象，而是声明"我需要什么"，Spring 容器在启动时注入给它。

---

## IoC 容器的工作流程

```
① Spring 启动 → 扫描包，找到所有 @Component/@Service/@Controller/@Repository
② 对每个找到的类，通过反射创建实例（Bean）
③ 扫描每个 Bean，找到 @Autowired 字段，注入对应的 Bean
④ 把所有 Bean 放到 IoC 容器中管理
⑤ 项目运行时，任何人都可以从容器中获取 Bean
```

---

## DI 的三种注入方式

```java
// ① 字段注入（最常用，@Autowired）
@Service
public class OrderService {
    @Autowired
    private UserService userService;
}

// ② Setter 注入
@Service
public class OrderService {
    private UserService userService;
    
    @Autowired
    public void setUserService(UserService userService) {
        this.userService = userService;
    }
}

// ③ 构造器注入（Spring 官方推荐）
@Service
public class OrderService {
    private final UserService userService;
    
    public OrderService(UserService userService) {  // 不用 @Autowired 也行
        this.userService = userService;
    }
}
```

**实际项目**：字段注入（`@Autowired`）最常见，简单直接。构造器注入适合必须依赖的场景，且便于单元测试。

---

## 为什么叫"控制反转"

**传统写法**：程序员主动控制——自己 `new` 对象，自己管理依赖。

**IoC 写法**：控制权反转给容器——程序员只声明需要什么，容器负责创建和注入。

```
传统：代码主动 new 对象 → "我要什么就自己造"
IoC：声明需要什么 → "我要什么你（容器）给我"
```

这使得代码之间的耦合度降低，换实现只需要换 Bean 的声明，不需要改动依赖它的代码。

---

## 项目关联

| 概念 | 在项目中的位置 |
|------|---------------|
| **IoC 容器** | Spring Boot 启动时自动创建，管理所有标记了 `@Service`/`@Controller` 等的类 |
| **DI（@Autowired）** | Controller 注入 Service，Service 注入 Mapper |
| **构造器注入** | 可以通过一个构造器参数列表清楚看到这个类依赖了什么 |
