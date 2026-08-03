---
publish: true
---

# MyBatisPlus 核心

---

## 核心

MyBatisPlus 是 MyBatis 的增强工具，提供了通用的 CRUD 方法、条件构造器和分页插件——你不需要自己写简单的增删改查 SQL。

---

## BaseMapper——内置通用方法

```java
public interface UserMapper extends BaseMapper<User> {
    // 继承 BaseMapper 后，以下方法直接可用，不用写 SQL
}

// 使用
userMapper.insert(user);                // 插入
userMapper.deleteById(1L);              // 根据 ID 删除
userMapper.updateById(user);            // 根据 ID 更新
userMapper.selectById(1L);              // 根据 ID 查询
userMapper.selectList(null);            // 查询全部
userMapper.selectPage(page, wrapper);   // 分页查询
```

**BaseMapper 提供的完整方法族**：

| 方法 | 用途 |
|------|------|
| `insert(T entity)` | 插入 |
| `deleteById(Serializable id)` | 按 ID 删除 |
| `deleteByMap(Map)` | 按条件 Map 删除 |
| `updateById(T entity)` | 按 ID 更新 |
| `update(T entity, Wrapper)` | 按条件更新 |
| `selectById(Serializable id)` | 按 ID 查 |
| `selectList(Wrapper)` | 按条件查列表 |
| `selectOne(Wrapper)` | 按条件查单个 |
| `selectCount(Wrapper)` | 按条件计数 |
| `selectPage(Page, Wrapper)` | 分页查询 |

---

## 条件构造器

```java
// QueryWrapper（直接用字段名，注意硬编码问题）
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("email", "test@test.com")
       .like("name", "张")
       .ge("age", 18)
       .orderByDesc("created_at");
userMapper.selectList(wrapper);

// LambdaQueryWrapper（推荐：类型安全，避免硬编码）
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(User::getEmail, "test@test.com")       // 不会写错字段名
       .like(User::getName, "张")
       .ge(User::getAge, 18)
       .orderByDesc(User::getCreatedAt);
userMapper.selectList(wrapper);
```

**常用条件方法**：

| 方法 | 说明 | SQL 效果 |
|------|------|---------|
| `eq` | 等于 | `WHERE name = '张三'` |
| `ne` | 不等于 | `WHERE name != '张三'` |
| `gt` / `ge` | 大于 / 大于等于 | `WHERE age > 18` |
| `lt` / `le` | 小于 / 小于等于 | `WHERE age < 60` |
| `like` | 模糊匹配 | `WHERE name LIKE '%张%'` |
| `in` | 在集合中 | `WHERE id IN (1,2,3)` |
| `isNull` | 为空 | `WHERE email IS NULL` |
| `between` | 范围 | `WHERE age BETWEEN 18 AND 60` |

---

## 分页插件

```java
// 配置分页插件
@Configuration
public class MyBatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(
            new PaginationInnerInterceptor(DbType.MYSQL)
        );
        return interceptor;
    }
}

// 使用
Page<User> page = new Page<>(1, 10);  // 第 1 页，每页 10 条
Page<User> result = userMapper.selectPage(page, wrapper);

result.getRecords();     // 当前页数据列表
result.getTotal();       // 总记录数
result.getCurrent();     // 当前页码
result.getPages();       // 总页数
result.getSize();        // 每页条数
```

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **基本 CRUD** | 继承 `BaseMapper` 后，单表增删改查不用写一行 SQL |
| **条件查询** | `LambdaQueryWrapper` 用于多条件组合查询 |
| **分页** | `Page` + `selectPage` 实现用户列表、消息列表分页 |
