# JavaWeb 基础

---

## 核心

JavaWeb 是 Spring Boot 的前身——理解了 Servlet 和 Filter，才能真正理解 Spring Boot 的请求处理流程。

---

## Tomcat——Web 容器

Spring Boot 内嵌了 Tomcat，所以不需要单独部署。它的作用：

```
浏览器 → HTTP 请求 → Tomcat（端口 8080）
                       ↓
                  分配线程处理请求
                       ↓
                  转发给 Servlet / Spring Boot
```

**不需要配置 Tomcat**（Spring Boot 内嵌了），只需要知道：
- 默认端口 8080，`server.port=8081` 可以改
- 每个请求由 Tomcat 线程池中的一个线程处理
- 请求走到 Spring Boot 之前，Tomcat 做了最底层的网络解析

---

## Servlet——处理 HTTP 请求的 Java 程序

在 JavaWeb 时代，每个 API 需要写一个 Servlet：

```java
// JavaWeb 时代（现在 Spring Boot 帮你做了）
@WebServlet("/hello")
public class HelloServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
        resp.getWriter().write("Hello");
    }
}
```

**Spring Boot 做的事**：你写的 `@RestController` + `@GetMapping`，本质上就是在注册 Servlet。`DispatcherServlet` 是 Spring Boot 的核心 Servlet，它负责分发请求到对应的 Controller 方法。

```
请求 → Tomcat → DispatcherServlet → 找对应的 Controller 方法 → 执行 → 返回响应
```

---

## Filter——过滤器

Filter 是 Servlet 规范中的组件，在请求到达 Servlet **之前**执行过滤逻辑：

```java
public class AuthFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, 
                         FilterChain chain) {
        // 请求到达 Controller 之前
        if (checkAuth(request)) {
            chain.doFilter(request, response);  // 放行
        } else {
            // 拦截
        }
        // Controller 执行完后返回时也会经过这里
    }
}
```

**Filter 的特性**：
- 作用范围广——拦截所有请求，包括静态资源、Servlet、JSP
- 基于 Servlet 规范，**不依赖 Spring**
- 在 Spring Boot 中通过 `@WebFilter` 或 `FilterRegistrationBean` 注册

---

## Filter 与拦截器的位置关系

```
请求 → Tomcat → Filter → DispatcherServlet → Interceptor → Controller
                         ↑                    ↑
                     Servlet 规范         Spring 的
                     Filter 先执行         Interceptor 后执行
```

**Filter 能做的事**：编码设置、CORS 跨域、请求日志（最通用的过滤）

**Interceptor 能做的事**：登录校验、权限控制、请求耗时统计（可以操作 Spring 的 Bean）

---

## 请求完整链路（从 Tomcat 到 Spring Boot）

```
① 浏览器发 HTTP 请求到 localhost:8080/api/users

② Tomcat 接收请求，分配线程

③ Filter 链处理
   ├→ CharacterEncodingFilter（设置 UTF-8）
   ├→ CorsFilter（跨域处理）
   └→ AuthFilter（自定义，校验 Token）

④ DispatcherServlet 接收请求，找对应的 Controller 方法

⑤ Interceptor.preHandle() 执行
   ├→ JwtAuthInterceptor（校验 JWT）
   ├→ RateLimitInterceptor（限流）
   └→ ProcessTimeInterceptor（记录耗时）

⑥ Controller 方法执行
   └→ Service → Mapper → 数据库

⑦ Interceptor.postHandle() / afterCompletion() 执行

⑧ DispatcherServlet 返回响应给客户端
```

---

## 项目关联

| 概念 | 在项目中的位置 |
|------|---------------|
| **Tomcat** | Spring Boot 内嵌，启动时自动运行，默认 8080 端口 |
| **DispatcherServlet** | Spring Boot 自动注册，负责分发请求到 Controller |
| **Filter** | 编码设置、CORS 跨域处理 |
| **请求完整链路** | 你的项目里拦截器链执行的路径就是这条链路 |
