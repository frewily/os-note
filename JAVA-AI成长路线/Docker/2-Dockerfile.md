# Dockerfile

---

## 核心

Dockerfile 是构建镜像的配方——把你的项目打包成一个可运行的镜像。

---

## 一个完整的 Dockerfile

```dockerfile
# 指定基础镜像（通常带 JDK 的最小镜像）
FROM eclipse-temurin:17-jre

# 维护者信息（可选）
LABEL maintainer="your@email.com"

# 设置工作目录
WORKDIR /app

# 复制 jar 包到镜像
COPY target/app.jar app.jar

# 暴露端口（只是声明，实际映射用 -p）
EXPOSE 8080

# 启动命令
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## 构建和运行

```bash
# 先确保项目已打包（target/app.jar 存在）
mvn clean package

# 构建镜像
docker build -t my-app:1.0 .
#   -t   镜像名称:标签
#   .    当前目录下的 Dockerfile

# 运行
docker run -d --name my-app -p 8080:8080 my-app:1.0
```

---

## 常用指令

| 指令 | 作用 | 例子 |
|------|------|------|
| `FROM` | 基础镜像 | `FROM eclipse-temurin:17-jre` |
| `WORKDIR` | 工作目录 | `WORKDIR /app` |
| `COPY` | 复制文件 | `COPY target/*.jar app.jar` |
| `RUN` | 构建时执行命令 | `RUN apt-get update` |
| `EXPOSE` | 声明端口 | `EXPOSE 8080` |
| `ENTRYPOINT` | 容器启动命令 | `ENTRYPOINT ["java", "-jar", "app.jar"]` |
| `ENV` | 环境变量 | `ENV JAVA_OPTS="-Xmx256m"` |

---

## 多阶段构建（减少镜像体积）

```dockerfile
# 第一阶段：编译
FROM eclipse-temurin:17-jdk AS builder
WORKDIR /build
COPY . .
RUN chmod +x mvnw && ./mvnw package -DskipTests

# 第二阶段：运行（只复制 jar，不包含 JDK 和源码）
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /build/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**效果**：最终镜像只包含 JRE 和 jar 包，体积从 500MB+ 降到 200MB 左右。

---

## .dockerignore

```dockerfile
# 和 .gitignore 一样，构建时忽略的文件
target/
.git/
.idea/
*.md
*.log
```
