---
publish: true
---

# MyBatis 基础

---

## 核心

MyBatis 是 Java 操作数据库的持久层框架，把你的 Java 接口和 SQL 映射起来——你写 SQL，MyBatis 帮你执行并转成对象。

---

## 为什么需要 ORM

```java
// ❌ JDBC 原生写法——每次都得写一堆重复代码
public User findById(Long id) {
    Connection conn = dataSource.getConnection();
    PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
    ps.setLong(1, id);
    ResultSet rs = ps.executeQuery();
    User user = new User();
    if (rs.next()) {
        user.setId(rs.getLong("id"));
        user.setName(rs.getString("name"));
        // ... 每个字段手动映射
    }
    rs.close(); ps.close(); conn.close();
    return user;
}

// ✅ MyBatis——只需要写 SQL 和接口
@Mapper
public interface UserMapper {
    @Select("SELECT * FROM users WHERE id = #{id}")
    User findById(Long id);
    // MyBatis 自动执行 SQL、把 ResultSet 映射成 User 对象
}
```

---

## Mapper 原理

```java
@Mapper  // 告诉 Spring：这是一个 MyBatis 映射器接口
public interface UserMapper {
    
    @Select("SELECT * FROM users WHERE id = #{id}")
    User findById(@Param("id") Long id);
    
    @Insert("INSERT INTO users(name, email) VALUES(#{name}, #{email})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);
}
```

**Spring Boot 启动时**：

```
① 扫描 @Mapper 接口
② 用 JDK 动态代理生成 Mapper 的代理对象
③ 代理对象中，每个方法绑定对应的 SQL
④ 调用 userMapper.findById(1) → 代理对象执行 SQL → 返回结果
```

**vibe coding 视角**：你写 `userMapper.findById(1)`，实际执行的是代理对象里的 SQL。所以 `@Mapper` 接口上没有实现代码也能工作。

---

## #{} vs ${}——最值得注意的差异

```sql
-- #{}：预编译，安全防 SQL 注入（绝大多数场景用这个）
@Select("SELECT * FROM users WHERE id = #{id}")
-- 实际执行：SELECT * FROM users WHERE id = ?
-- 参数通过 ? 占位传入，无论参数是什么都不会破坏 SQL 结构

-- ${}：字符串拼接，不安全（仅在动态表名/列名时用）
@Select("SELECT * FROM ${tableName} WHERE id = #{id}")
-- 实际执行：SELECT * FROM users WHERE id = ?
-- 表名是拼进去的，有 SQL 注入风险
```

**基本原则**：能用 `#{}` 就不用 `${}`。只有在表名、列名等 SQL 结构需要动态传入时才用 `${}`，且确保传入的值是安全的（如枚举或配置）。

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **UserMapper 接口** | `@Mapper` + `@Select` / `@Insert` 注解定义操作 |
| **参数传递** | 单个参数直接传，多个参数用 `@Param` |
| **主键回填** | 插入后获取自增 ID，用 `@Options(useGeneratedKeys = true)` |
