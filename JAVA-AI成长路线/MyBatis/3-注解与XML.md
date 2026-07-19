# 注解与 XML

---

## 核心

注解适合简单 SQL，XML 适合复杂 SQL——可以混用，同一项目中两种风格并存是常见做法。

---

## 注解方式

```java
@Mapper
public interface UserMapper {
    
    @Select("SELECT * FROM users WHERE id = #{id}")
    User findById(Long id);
    
    @Insert("INSERT INTO users(name, email) VALUES(#{name}, #{email})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);
    
    @Update("UPDATE users SET name = #{name} WHERE id = #{id}")
    int update(User user);
    
    @Delete("DELETE FROM users WHERE id = #{id}")
    int deleteById(Long id);
}
```

**适用场景**：单表简单 CRUD、字段少的查询。MP 的 `BaseMapper` 连这个都不用写。

---

## XML 方式

```java
@Mapper
public interface UserMapper {
    User findById(Long id);
    List<User> searchUsers(@Param("keyword") String keyword, 
                           @Param("status") Integer status);
    void insertBatch(@Param("list") List<User> users);
}
```

```xml
<!-- resources/mapper/UserMapper.xml -->
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">
    
    <!-- 结果映射 -->
    <resultMap id="UserResultMap" type="User">
        <id property="id" column="id"/>
        <result property="name" column="name"/>
        <result property="email" column="email"/>
    </resultMap>
    
    <!-- 简单查询 -->
    <select id="findById" resultMap="UserResultMap">
        SELECT * FROM users WHERE id = #{id}
    </select>
    
    <!-- 多条件查询 -->
    <select id="searchUsers" resultMap="UserResultMap">
        SELECT * FROM users
        <where>
            <if test="keyword != null and keyword != ''">
                AND (name LIKE CONCAT('%', #{keyword}, '%')
                     OR email LIKE CONCAT('%', #{keyword}, '%'))
            </if>
            <if test="status != null">
                AND status = #{status}
            </if>
        </where>
    </select>
    
    <!-- 批量插入 -->
    <insert id="insertBatch">
        INSERT INTO users(name, email) VALUES
        <foreach collection="list" item="item" separator=",">
            (#{item.name}, #{item.email})
        </foreach>
    </insert>
    
</mapper>
```

**注意**：XML 文件放在 `resources/mapper/` 目录下，并在 `application.yml` 中配置扫描路径：

```yaml
mybatis-plus:
  mapper-locations: classpath:mapper/**/*.xml
```

---

## 什么时候用注解，什么时候用 XML

| 场景 | 推荐 | 理由 |
|------|------|------|
| 单表简单 CRUD | 注解 / MP BaseMapper | 不需要自己写 SQL |
| 多表 JOIN 查询 | XML | SQL 太长，放在 XML 中更清晰 |
| 动态条件复杂（if/choose/foreach） | XML | XML 的 `<if>` `<where>` 标签更强大 |
| SQL 字段多，需要复用 | XML | 可以定义 `<sql>` 片段，多处引用 |
| 简单查询，就一两行 SQL | 注解 | 不需要单独开 XML 文件 |

**vibe coding 视角**：AI 对注解方式生成更准确，复杂查询建议让 AI 生成 XML 中的 SQL。也可以在 prompt 中说明"把复杂 SQL 写在 XML 中"。

---

## @Param——多参数传递

```java
// 多个参数，必须用 @Param 指定名称
@Select("SELECT * FROM users WHERE name = #{name} AND age = #{age}")
User findByNameAndAge(@Param("name") String name, @Param("age") Integer age);
```

单个参数不需要 `@Param`，MyBatis 能自动识别。多个参数时如果不加 `@Param`，MyBatis 会用 `arg0`、`arg1` 作为默认名称——所以**建议多参数时统一加 @Param**。

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **简单 CRUD** | MP BaseMapper 搞定，不用写 SQL |
| **多表联查** | XML 写 JOIN 查询，清晰可维护 |
| **动态条件搜索** | XML `<if>` 标签实现可选的查询条件 |
| **批量操作** | XML `<foreach>` 实现批量插入或更新 |
