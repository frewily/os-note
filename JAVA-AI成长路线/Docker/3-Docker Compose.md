---
publish: true
---

# Docker Compose

---

## 核心

Compose 用 YAML 文件定义多个容器的启动方式，一条命令全部拉起——项目需要同时跑 MySQL + Redis + 应用时用。

---

## docker-compose.yml

```yaml
version: '3.8'

services:
  # 应用服务
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_DATASOURCE_URL=jdbc:mysql://db:3306/ai_chat
      - SPRING_REDIS_HOST=redis
    depends_on:
      - db
      - redis

  # MySQL
  db:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=123456
      - MYSQL_DATABASE=ai_chat
    volumes:
      - mysql_data:/var/lib/mysql

  # Redis
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
```

**注意**：Compose 中服务名可以作为主机名通信。应用里连接数据库写 `jdbc:mysql://db:3306`，不用写 `localhost`。

---

## 常用命令

```bash
# 启动所有服务
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f app

# 进入容器
docker compose exec app bash

# 重启特定服务
docker compose restart app

# 停止所有服务
docker compose stop

# 停止并删除所有容器和网络
docker compose down

# 停止并删除数据卷（⚠️ 数据库数据也会删）
docker compose down -v

# 重新构建镜像后启动（改代码后常用）
docker compose up -d --build
```

---

## 开发 vs 生产

| | 开发环境 | 生产环境 |
|--|---------|---------|
| 数据库 | Compose 里一起跑 | 单独的数据库服务 |
| 构建 | 本地 build | CI/CD 构建 |
| 配置 | `.env` 文件 | 环境变量/配置中心 |

**开发时**：一个 `docker compose up -d` 就把全套环境拉起来。

**生产中**：数据库和 Redis 由运维管理，应用单独用 Docker 部署。但 Compose 文件仍然可以用来定义应用启动方式。
