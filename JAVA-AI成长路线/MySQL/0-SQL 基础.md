# SQL 基础

---

## 核心

SQL 是操作数据库的语言，核心操作是 CURD——AI 生成 SQL 时，你主要需要判断查询逻辑是否正确。

---

## SELECT 执行顺序

SQL 的书写顺序和执行顺序不同，理解执行顺序有助于判断 AI 生成的查询是否合理。

```sql
-- 书写顺序
SELECT  字段                      -- ⑤
FROM    表                        -- ①
JOIN    关联表                     -- ②
WHERE   过滤条件                   -- ③
GROUP BY 分组字段                  -- ④
HAVING  分组后过滤                 -- ⑥
ORDER BY 排序字段                  -- ⑦
LIMIT   限制条数                   -- ⑧

-- 实际执行顺序
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

**vibe coding 视角**：看到 AI 生成的 SQL 中有 WHERE 里用聚合函数（如 `WHERE count > 1`），应意识到这不可能——聚合发生在 GROUP BY 之后，应改用 HAVING。

---

## JOIN——AI 最容易用错的地方

```sql
-- INNER JOIN：两张表都有才返回（最常用）
SELECT * FROM orders o
INNER JOIN users u ON o.user_id = u.id;

-- LEFT JOIN：左表全保留，右表没有则为 NULL
SELECT * FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN：右表全保留（基本可以换成 LEFT JOIN 避免混淆）
SELECT * FROM orders o
RIGHT JOIN users u ON o.user_id = u.id;   -- 等价于上面的 LEFT JOIN

-- FULL OUTER JOIN：两边都全保留（MySQL 不直接支持）
```

**INNER vs LEFT 的选择**：
- 两个表都**必须存在**匹配记录 → INNER JOIN
- 主表记录**无论是否匹配**都要保留 → LEFT JOIN

**vibe coding 视角**：AI 经常在不该用 LEFT JOIN 的地方用 LEFT JOIN，结果多出预期外的 NULL 行。看到 LEFT JOIN 时检查业务逻辑是否真的需要主表全保留。

---

## GROUP BY + 聚合

```sql
-- 按用户统计订单数
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id;

-- 筛选订单数 > 5 的用户
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING order_count > 5;    -- WHERE 不行，聚合后只能用 HAVING
```

**常见规则**：SELECT 中的非聚合字段，必须出现在 GROUP BY 中。SQL 严格模式下不遵守会报错。

---

## 子查询 vs JOIN

```sql
-- 子查询（直观但可能慢）
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 100);

-- 等价 JOIN（通常更优）
SELECT DISTINCT u.*
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.amount > 100;
```

**vibe coding 视角**：AI 倾向于生成子查询，因为逻辑更直观。如果查询较慢，可以考虑改写成 JOIN 看是否提升。不是所有子查询都比 JOIN 慢——具体看执行计划。

---

## WHERE vs HAVING

| | WHERE | HAVING |
|--|-------|--------|
| 执行时机 | GROUP BY 之前 | GROUP BY 之后 |
| 可使用 | 普通字段条件 | 聚合函数条件 |
| 性能 | 先过滤再聚合，更高效 | 先聚合再过滤 |

**原则**：能在 WHERE 里过滤的，不要放到 HAVING 里。

---

## vibe coding 视角总结

AI 生成的 SQL 通常在语法上正确，但逻辑上可能有问题：

- JOIN 类型是否选对（INNER vs LEFT 最常见错误）
- WHERE 和 HAVING 是否混用
- 子查询是否可以优化为 JOIN
- SELECT 的字段是否都在 GROUP BY 中（严格模式会报错）

不需要记忆 SQL 函数的细节——需要时直接让 AI 生成或查文档。

---

## 项目关联

| 场景 | 说明 |
|------|------|
| **AI 客服的消息记录查询** | 按用户分组统计对话次数、平均 Token 消耗 |
| **用户权限查询** | 多表 JOIN（user → role → permission）|
| **订单统计** | GROUP BY 按状态、按时间分组统计 |
