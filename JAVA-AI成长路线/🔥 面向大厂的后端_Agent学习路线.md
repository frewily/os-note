---
publish: true
title: "🔥 面向大厂的后端/Agent学习路线"
source: "https://www.yuque.com/casanova-6avif/tq9y2x/lxu6dp5g189zu6da?singleDoc#"
author:
published: true
created: 2026-07-14
description:
tags:
  - "clippings"
---

## 关联知识点

- [[JAVA-AI成长路线/00-知识地图]] — 返回顶层入口

---

一.背景

很多同学在刚学习计算机内容，或是刚转码时，肯定一头雾水，不知道计算机专业就业有哪些方向、应该学哪些内容。因此，我会用自己学习多年的踩坑点和学习经验，争取帮大家扫清知识盲区，用面向大厂就业的标准，给大家分享可行性高的学习路线

并且，在当前AI时代下，不建议大家再去看几年前的学习路线。AI已经重构了行业的很多既往规则，现在学习技术也一定要结合AI大趋势，才能更有竞争力

就业方向

1

算法：门槛最高（985/211硕博起步），待遇最好，但学历和学术要求极高

2

后端开发/agent开发：门槛相对高，待遇不错，被AI替代的风险目前不高，综合最为推荐

3

前端开发：门槛一般，但存在AI替代危机，不建议学纯前端

4

客户端开发/测试开发：校招门槛较低，很多大厂接受0基础转客户端，但社招很难跳槽

5

运维：门槛较低，但含金量也较低，且hc极少，很少从校招招人

分享重点

由于我本人是做后端/agent开发，因此只对这部分学习路线做分享

国内后端开发的常用编程语言是Java/Golang，目前还是以Java为主（如阿里/京东/美团等），但近几年越来越多大厂开始转向使用Golang（如腾讯/字节/百度等）。不过综合还是推荐学习Java，一是国内Java的学习资料比较完善，各种视频和文档都能找到，更容易学；二是使用Golang的大厂也能接受使用Java面试，进公司后再转Golang，因此不用担心语言不匹配的问题

在当今AI大趋势下，一定不能只学习传统的后端开发内容，一定要学习AI知识，从基础的

MCP

/

SKILLs

/

RAG

等概念，到具体使用

SpringAI

/

Langchain4j

等框架搭建Agent，都有必要学习，才能让自己更有竞争力

二.传统Java开发

传统Java开发内容主要分为三部分，

●

Java相关内容（Java/JavaWeb/Spring相关框架/Mybatis相关框架等）

●

常用中间件（MySQL/Redis/MQ等）

●

开发必备工具（Maven/Git/Docker等）

初期可以观看视频学习，无需手敲太多代码，主要是积累知识。中后期建议直接看文档学习，效率更高，必要的内容可以手敲熟悉一下（如常用中间件的使用/项目代码等）

2.1 Java相关

1

Java基础

学习Java的基本语法和特性，适合新手入门，课程略微啰嗦，建议倍速，只看关键点，也可以看文档自行学习[Java上](https://www.bilibili.com/video/BV17F411T7Ao/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)[Java下](https://www.bilibili.com/video/BV1yW4y1Y7Ms/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)

2

JavaWeb

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009116940-4a9f5e77-e5c5-4f56-b331-9759de33fbf2.png)

已过时的技术，但是是现在Spring框架的基础，学习了解一下即可，如果赶时间也可以跳过[JavaWeb](https://www.bilibili.com/video/BV1Z3411C7NZ/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)

3

Spring框架系列

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009223478-ba195b1c-d694-4437-9ce3-c7086d969c49.png) ![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009294735-f2fbb0ce-b77a-4e7a-af47-2fa2f3ea12a6.png)

现在Java开发的核心框架，尤其是Springboot+SpringMVC+Mybatis，必须重点学习[Spring](https://www.bilibili.com/video/BV1Ft4y1g7Fb/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)[SpringMVC](https://www.bilibili.com/video/BV1sC411L76f/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)[SpringBoot](https://www.bilibili.com/video/BV15b4y1a7yG/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)

4

Mybatis系列

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009377600-b7e9d11f-28a7-4a1c-935f-6bdffbdb7d8f.png)

Mybatis是现在最常用的持久层框架，通常和Spring系列框架结合使用，MybatisPlus是优化版，新增一些功能[Mybatis](https://www.bilibili.com/video/BV1JP4y1Z73S/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)[MybatisPlus](https://www.bilibili.com/video/BV1Xu411A7tL/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)

2.2 常用中间件

1

MySQL

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009504286-1b92aae8-efc5-4608-8df4-1863e696a2b5.png)

国内最常用的数据库是MySQL，十分重要！

刚开始只学习基础操作，会用即可，后期再结合八股学习进阶应用和集群架构等[MySQL](https://www.bilibili.com/video/BV1Kr4y1i7ru/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)

2

Redis

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009592310-5e5cea3f-412d-4854-829b-0573a20e96e1.png)

Redis是国内最常用的缓存中间件，常用于应对高并发场景

同样刚开始会用即可，后期再结合八股进阶学习[Redis](https://www.bilibili.com/video/BV1cr4y1671t/?share_source=copy_web&vd_source=63a2d3717f2d0893e41eca3fa30b6d20)

3

MQ

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009672523-59ac54ce-a819-4e69-9ede-6b72c8b9fd3a.png)

MQ是消息队列，也是非常重要的中间件

国内企业常用RocketMQ/Kafka，而RabbitMQ的性能相对较差，使用较少

入门建议从RocketMQ/Kafka中选择其一学习即可

4

ElasticSearch

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776009880644-0e56e377-6817-4f97-990a-46dcef0795ed.png)

ES是一款搜索引擎中间件，相比MySQL，可以实现更多样的搜索功能，常用于电商场景，也需要重点学习

2.3 开发必备工具

1

Maven

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776010068887-651cd185-cf17-479f-a2d3-664573131089.png)

Maven是Java开发必备的管理工具，可以便捷地管理开发所需的依赖，需要重点学习！

2

Git

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776010121012-cdd0dc0e-f9e4-4843-9e58-43ca87538743.png)

Git也是开发必备的代码管理工具，入门只需学习基础操作即可，后面再在实践中学习分支管理等操作

3

Linux

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776010143205-1194743a-4508-4f65-b5da-e51f51b0778d.png)

由于实际开发时通过使用服务器终端进行操作，因此需要熟悉Linux系统的基础指令，提升开发效率

4

Docker

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776010167812-2bba301a-61dc-460b-a340-c2b320c97888.png)

将项目部署到服务器上线时，需要借助docker，便捷地管理中间件

2.4 项目

以上内容都学习之后，可以学习一些入门项目，熟悉开发流程

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776010414266-1a763ac6-66db-4615-82c7-7a9ad91d1817.png)

我还是比较推荐黑马程序员的苍穹外卖和黑马点评项目，虽然已经烂大街了，但作为新手入门学习还是很有帮助的。敲完这两个项目之后，可以再自己在B站/知识星球等渠道找一些免费/付费的进阶项目，熟悉一下微服务的操作。本次分享主要针对新手入门场景，就不再做具体的进阶推荐

三.AI相关内容

以上这套传统的Java学习路线是我两年前学习Java时的路线，作为开发岗的基础打底很有用，但在如今的AI大趋势下，显得太过单薄和死板

因此，在以上基础上，我根据自己面试和实习的感悟，整理了一些AI方向必学的重要知识，建议大家认真学习实践，提升面试的竞争力，同时也能够投递更多方向的岗位，如Agent开发岗等，而非局限于传统的后端开发岗

3.1 AI概念扫盲

📒

可以根据企业官网AI/Agent相关岗位的职位描述，找到对应的概念针对性学习

以阿里官网的AI应用研发工程师这个实习岗位为例，可以看到，核心是RAG和围绕RAG上下游的一系列工程，包括

Context Engieering

、

Prompt Engieering

、

Tool Calling

、

MCP

、

SKills

等，这些都是目前AI发现的新概念，也是重要概念

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776489553946-8c9948c7-96f8-4fcd-a003-4364b1ed25eb.png)

至于具体去哪儿学这些知识呢？

1

可以去Anthropic、OpenAI之类的AI巨头的官网学习，毕竟AI的很多新概念就是它们提出的，如

SKills

这个概念就是由Anthropic提出的，直接去看它们官网的原文文档肯定是最精准、最详细的

2

但是由于这些AI巨头基本都是美国的，使用英语，对中文环境的我们学习起来不太友好，而且可能内容太过详细了，反而不便于入门。因此，也可以在国内的

B站

、

CSDN

、

知识星球

之类的平台分别搜索这些概念学习。目前国内平台上有很多优质的AI圈up主，视频质量非常高，作为入门绝对够

3.2 AI项目实践

1

入门项目：如果只是想入门Agent开发，熟悉基本流程，可以看黑马程序员的入门视频，大致熟悉SpringAI/Langchain4j这些AI应用框架的用法。但这些项目只能算demo，其规模和完成度不足以算作一个完整的可以写入简历的项目，可以考虑将其加入自己已经做好的项目中

例如，在苍穹外卖里引入AI搭建一个点餐信息的AI智能客服，作为一个技术亮点

![image.png](https://cdn.nlark.com/yuque/0/2026/png/48787347/1776490092786-1db10d67-6ea8-40b0-b651-a53058be36b7.png)

2

成型项目：由于目前AI技术迭代特别快，暂时没有发现很完整的成型项目，可以自行把学到的知识融合实践，把以上的demo项目迭代优化成大型项目