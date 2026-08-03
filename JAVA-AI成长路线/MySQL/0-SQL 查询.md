---
publish: true
---

# SQL 查询

---

## 核心

SELECT 是 SQL 中使用频率最高的操作，核心是"从哪些表、过滤什么条件、返回什么字段"。

---

## 基本 SELECT

```sql
-- 查询所有列（仅临时查询用，代码中不要用）
SELECT * FROM users;

-- 查询指定列
SELECT id, name, email FROM users;

-- 列起别名（AS 可省略）
SELECT name AS 用户名, email FROM users;

-- 去重
SELECT DISTINCT status FROM orders;
```

---

## WHERE——过滤条件

```sql
-- 比较运算符
WHERE age > 18
WHERE amount >= 100
WHERE status != 0

-- 多个条件组合
WHERE status = 1 AND age > 18
WHERE status = 1 OR   vip_level > 3

-- IN——匹配列表中的任意值
WHERE status IN (1, 2, 3)

-- BETWEEN——范围（闭区间，包含两端）
WHERE age BETWEEN 18 AND 60        -- 等价于 age >= 18 AND age <= 60

-- LIKE——模糊匹配
WHERE name LIKE '张%'               -- % 匹配任意多个字符
WHERE name LIKE '张_'               -- _ 匹配单个字符

-- NULL 判断（不能用 = NULL）
WHERE email IS NULL                 -- email 为空
WHERE email IS NOT NULL             -- email 不为空
```

**常见坑**：`WHERE email = NULL` 永远不成立——NULL 的比较必须用 `IS NULL`。

---

## ORDER BY——排序

```sql
-- 升序（ASC 默认，可省略）
SELECT * FROM users ORDER BY created_at;

-- 降序
SELECT * FROM users ORDER BY created_at DESC;

-- 多字段排序（先按 status 升序，同 status 再按 created_at 降序）
SELECT * FROM orders ORDER BY status ASC, created_at DESC;
```

---

## LIMIT——分页

```sql
-- 取前 10 条
SELECT * FROM users LIMIT 10;

-- 跳过 20 条，取 10 条（第 3 页，每页 10 条）
SELECT * FROM users LIMIT 10 OFFSET 20;

-- 简写语法（效果一样）
SELECT * FROM users LIMIT 20, 10;   -- 先偏移量，再取数量
```

**OFFSET 在数据量大时性能会下降**——因为数据库还是要扫描被跳过的行。大数据量分页通常用"游标分页"（WHERE id > ? LIMIT 10）替代。

---

## 聚合函数

```sql
COUNT(*)         -- 行数
SUM(amount)      -- 总和
AVG(price)       -- 平均值
MAX(created_at)  -- 最大值（如最新时间）
MIN(created_at)  -- 最小值（如最早时间）

-- 示例
SELECT COUNT(*) FROM users WHERE status = 1;
SELECT AVG(amount) FROM orders WHERE user_id = 1;
```

---

## GROUP BY——分组统计

```sql
-- 按状态统计订单数
SELECT status, COUNT(*) AS count
FROM orders
GROUP BY status;

-- 按年-月统计销售额
SELECT DATE_FORMAT(created_at, '%Y-%m') AS month,
       SUM(amount) AS total
FROM orders
GROUP BY month
ORDER BY month;
```

**要点**：SELECT 中的非聚合字段必须出现在 GROUP BY 中。

---

## HAVING——分组后过滤

```sql
-- WHERE 不行，因为聚合发生在 GROUP BY 之后
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING order_count > 5;
```

| | WHERE | HAVING |
|--|-------|--------|
| 执行时机 | GROUP BY 之前 | GROUP BY 之后 |
| 可以使用 | 普通字段 | 聚合函数 |
| 效率 | 更高（先过滤后分组） | 相对低（先分组后过滤） |

**原则**：能在 WHERE 里过滤的，不要放到 HAVING 里。

---

## JOIN——多表关联

```sql
-- INNER JOIN：两表都有匹配才返回
SELECT u.name, o.amount, o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN：左表全保留，右表无匹配则为 NULL
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
-- 结果包含所有用户，没有下单的用户 order 字段为 NULL

-- 多表 JOIN
SELECT u.name, o.amount, p.name AS product_name
FROM users u
INNER JOIN orders o    ON u.id = o.user_id
INNER JOIN products p  ON o.product_id = p.id;
```

**INNER vs LEFT 的选择**：
- 需要主表记录**全部保留** → LEFT JOIN
- 只需要**两表都有**匹配 → INNER JOIN

---

## 子查询

```sql
-- WHERE 中的子查询
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);

-- FROM 中的子查询（当作临时表）
SELECT AVG(order_count) FROM (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
) AS t;
```

**vibe coding 视角**：AI 倾向于生成子查询（逻辑直观）。执行慢时可以尝试改写成 JOIN 对比性能。

---

## UNION——合并查询结果

```sql
-- 合并两个查询结果（去重）
SELECT name, email FROM users
UNION
SELECT name, email FROM deleted_users;

-- UNION ALL 不去重，更快
SELECT name, email FROM users
UNION ALL
SELECT name, email FROM deleted_users;
```

**要求**：两个 SELECT 的列数必须相同，对应列的类型要兼容。

---

## 执行顺序

```sql
SELECT  字段                      -- ⑤
FROM    表                        -- ①
JOIN    关联表                     -- ②
WHERE   过滤条件                   -- ③
GROUP BY 分组字段                  -- ④
HAVING  分组后过滤                 -- ⑥
ORDER BY 排序字段                  -- ⑦
LIMIT   限制条数                   -- ⑧
```

理解这个顺序能帮你判断"为什么这里的条件不能这么写"（如 WHERE 不能写聚合函数）。

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **用户列表分页** | SELECT + WHERE 条件 + ORDER BY + LIMIT/OFFSET |
| **多表权限查询** | user → user_role → role → role_permission 多表 JOIN |
| **订单统计** | GROUP BY 按日期/状态分组统计 |
| **消息记录查询** | LEFT JOIN 用户表和对话表，查最近 N 条记录 |
