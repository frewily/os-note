---
publish: true
---

# SQL 操作与数据类型

---

## 核心

INSERT / UPDATE / DELETE 是写操作，CREATE TABLE 是建表——AI 生成的代码里你会经常看到，需要能看懂并在执行前判断是否安全。

---

## INSERT——插入数据

```sql
-- 插入完整一行（values 顺序与字段定义一致）
INSERT INTO users VALUES (1, '张三', 'zhangsan@email.com', NOW());

-- 指定字段插入（推荐，顺序自由，可读性好）
INSERT INTO users (name, email, created_at)
VALUES ('张三', 'zhangsan@email.com', NOW());

-- 批量插入（比逐条插入快很多）
INSERT INTO users (name, email) VALUES
('张三', 'zhangsan@email.com'),
('李四', 'lisi@email.com'),
('王五', 'wangwu@email.com');
```

---

## UPDATE——更新数据

```sql
-- 更新单条（务必带 WHERE，否则更新全表）
UPDATE users SET email = 'new@email.com' WHERE id = 1;

-- 更新多条
UPDATE orders SET status = 'cancelled'
WHERE status = 'pending' AND created_at < '2026-01-01';
```

**⚠️ 最常见事故**：忘记写 WHERE → 全表被更新。AI 生成的 UPDATE 执行前，第一眼看 WHERE 条件。

---

## DELETE——删除数据

```sql
-- 删除指定行
DELETE FROM users WHERE id = 1;

-- 清空表（不可回滚，速度比 DELETE 快）
TRUNCATE TABLE users;

-- 删除全部行（可回滚，但慢）
DELETE FROM users;
```

**⚠️ 同样：忘记 WHERE = 删全表。**

---

## 常用数据类型

```sql
CREATE TABLE users (
    id          BIGINT          PRIMARY KEY AUTO_INCREMENT,  -- 主键，自增
    name        VARCHAR(50)     NOT NULL,                    -- 变长字符串
    email       VARCHAR(100)    UNIQUE,                      -- 唯一约束
    age         INT             DEFAULT 0,                   -- 整数，默认值
    price       DECIMAL(10,2),                                -- 金额精确类型
    status      TINYINT         DEFAULT 0,                   -- 状态枚举（0/1/2）
    created_at  DATETIME        DEFAULT CURRENT_TIMESTAMP,   -- 创建时间
    updated_at  DATETIME        DEFAULT CURRENT_TIMESTAMP
                              ON UPDATE CURRENT_TIMESTAMP,   -- 更新时间（自动更新）
    deleted     TINYINT         DEFAULT 0                    -- 逻辑删除标记
);
```

**常用类型速查**：

| 类型 | 用途 | 说明 |
|------|------|------|
| `BIGINT` | 主键 ID | 自增主键用，范围足够大 |
| `VARCHAR(n)` | 字符串 | n 为最大字符数，如 `VARCHAR(50)` |
| `TEXT` | 长文本 | 文章内容、JSON 等，无默认值问题 |
| `INT` | 整数 | 一般计数用 |
| `DECIMAL(m,n)` | 金额 | m 总位数，n 小数位，如 `DECIMAL(10,2)` |
| `DATETIME` | 时间 | 带时区用 `TIMESTAMP` |
| `TINYINT` | 状态/布尔 | 0/1/2 等枚举值 |

---

## ALTER TABLE——改表结构

```sql
-- 加字段
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;

-- 改字段类型
ALTER TABLE users MODIFY COLUMN phone VARCHAR(30);

-- 加索引
ALTER TABLE users ADD INDEX idx_email (email);
```

**vibe coding 视角**：AI 经常在改表结构中生成 `AFTER` 子句来指定字段位置，这在生产环境大表上可能锁表。生产环境的表结构变更需要评估影响，不能直接执行 AI 生成的 ALTER TABLE。

---

## 常用函数

```sql
-- 字符串
CONCAT(first_name, ' ', last_name)   -- 拼接
LENGTH(name)                          -- 字符串长度
SUBSTRING(content, 1, 100)            -- 截取

-- 日期
NOW()                                 -- 当前时间
DATE(created_at)                      -- 取日期部分
DATE_FORMAT(created_at, '%Y-%m')      -- 格式化为"年-月"
TIMESTAMPDIFF(DAY, start, end)        -- 两个时间相差的天数

-- 条件
COALESCE(phone, email, '无联系方式')    -- 返回第一个非 NULL
IFNULL(phone, '无')                   -- phone 为 NULL 时返回默认值
CASE WHEN status = 1 THEN '启用'
     ELSE '禁用' END                  -- 条件表达式
```

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **AI 客服消息入库** | INSERT 批量写入对话记录 |
| **用户状态更新** | UPDATE ... WHERE id = ? 更新用户信息 |
| **逻辑删除** | 用 UPDATE 设置 deleted=1 代替 DELETE |
| **建表** | 根据业务需求设计字段类型和约束 |
