---
publish: true
---

# pom.xml 配置

---

## 核心

pom.xml 除了依赖，还有 parent、properties、profiles 等配置，用于统一管理和灵活切换构建环境。

---

## parent——继承父项目

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
    <relativePath/>
</parent>
```

**继承了什么**：
- `dependencyManagement` — 所有 Spring Boot 依赖的版本号（引入时不用写 version）
- `pluginManagement` — 插件的统一配置
- 默认的 Java 版本、编码方式等

**项目也可以自己写 parent**：多个子模块共享版本号时，自定义一个父 pom。

---

## properties——统一管理版本号

```xml
<properties>
    <java.version>17</java.version>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    
    <!-- 自定义版本变量 -->
    <mybatis-plus.version>3.5.5</mybatis-plus.version>
    <hutool.version>5.8.25</hutool.version>
</properties>
```

```xml
<!-- 引用变量 -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>${mybatis-plus.version}</version>   <!-- 引用上边的变量 -->
</dependency>
```

**好处**：升级版本只改一个地方，不需要全局搜索替换。

---

## profiles——多环境切换

```xml
<profiles>
    <!-- 开发环境 -->
    <profile>
        <id>dev</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <env>dev</env>
        </properties>
    </profile>
    
    <!-- 生产环境 -->
    <profile>
        <id>prod</id>
        <properties>
            <env>prod</env>
        </properties>
    </profile>
</profiles>
```

```bash
# 打包时指定环境
mvn clean package -Pprod
```

Spring Boot 项目更常用 application.yml 的多文档块或 `application-{env}.yml` 来切换环境，Maven profiles 用来控制不同环境下引用的依赖或插件配置。

---

## 常用插件

```xml
<build>
    <plugins>
        <!-- Spring Boot 打包插件（打为可执行 jar） -->
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
        
        <!-- 编译插件（指定 Java 版本） -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <configuration>
                <source>17</source>
                <target>17</target>
            </configuration>
        </plugin>
    </plugins>
</build>
```

| 插件 | 作用 |
|------|------|
| `spring-boot-maven-plugin` | 打可执行 jar（包含内嵌 Tomcat） |
| `maven-compiler-plugin` | 编译，指定 Java 版本 |
| `maven-surefire-plugin` | 运行测试 |
| `maven-jar-plugin` | 打 jar 包 |
| `maven-source-plugin` | 打包源码 |

---

## 完整 pom.xml 骨架

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>
    
    <groupId>com.example</groupId>
    <artifactId>ai-chat</artifactId>
    <version>1.0.0</version>
    <name>AI Chat</name>
    
    <properties>
        <java.version>17</java.version>
        <mybatis-plus.version>3.5.5</mybatis-plus.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
            <version>${mybatis-plus.version}</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```
