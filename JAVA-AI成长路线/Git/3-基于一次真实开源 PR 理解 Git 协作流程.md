---
publish: true
---
# 基于一次真实开源 PR 理解 Git 协作流程

> 本笔记基于一次真实的开源贡献经历整理。  
> 项目：`Chiu-xaH/Fuck-Yangtze-RainClassroom`  
> 我的 Fork：`frewily/Fuck-Yangtze-RainClassroom`
> 
> 核心目的不是背 Git 命令，而是理解：**AI 在执行 Git 操作时，到底在修改什么。**

---

## 1. 这次实践经历的整体流程

这次完整经历了：

```
原作者仓库
   ↓ Fork
我的 GitHub 仓库
   ↓ Clone
本地仓库
   ↓ 修改代码
commit
   ↓
push 到自己的 Fork
   ↓
Pull Request
   ↓
维护者 Code Review
   ↓
整理提交历史 / 缩小 PR 范围
   ↓
force push 更新 PR
   ↓
维护者 Merge
   ↓
代码正式进入 upstream/main
```

其中又经历了两个 PR：

```
PR #3
↓
提交历史比较混乱
混入 GitHub Actions 自动生成的日志提交
↓
关闭

重新从 upstream/main 建立干净分支
↓
cherry-pick 真正有用的提交
↓
PR #4
↓
维护者要求进一步缩小范围
↓
reset + force push
↓
PR #4 Merge
```

---

# 2. Fork 和 Clone 到底有什么区别？

这是开源贡献最开始的两个操作。

## Fork

Fork 是：

> **把别人的 GitHub 仓库复制一份到自己的 GitHub 账号下。**

原仓库：

```
Chiu-xaH/Fuck-Yangtze-RainClassroom
```

Fork 后：

```
frewily/Fuck-Yangtze-RainClassroom
```

为什么需要 Fork？

因为我不是原仓库维护者，没有权限直接执行：

```
git push 原作者仓库
```

所以正常开源协作方式是：

```
别人的仓库
↓ Fork
我自己的仓库
↓ 修改
向别人提 PR
```

---

## Clone

Clone 则是：

> **把 GitHub 上的仓库下载到自己的电脑。**

例如：

```
GitHub
frewily/Fuck-Yangtze-RainClassroom

        ↓ clone

Mac 本地
/Users/.../projects/Fuck-Yangtze-RainClassroom
```

所以：

```
Fork：GitHub → GitHub
Clone：GitHub → 本地电脑
```

---

# 3. origin 和 upstream 是什么？

这是这次最容易混淆的地方。

它们都不是分支，而是：

> **remote（远程仓库）的名字。**

通常：

```
origin
= 我自己的 Fork

upstream
= 原作者仓库
```

对应本次项目：

```
origin
→ frewily/Fuck-Yangtze-RainClassroom

upstream
→ Chiu-xaH/Fuck-Yangtze-RainClassroom
```

因此：

```
git fetch upstream
```

可以理解为：

> 获取原作者仓库的最新 Git 信息。

而：

```
git push origin xxx
```

表示：

> 把我的本地分支 `xxx` 推送到我自己的 GitHub Fork。

---

# 4. `main`、`origin/main`、`upstream/main` 有什么区别？

这几个名字看起来很像，但层级完全不同。

```
main
```

是：

> 我的本地分支。

---

```
origin/main
```

表示：

> 我自己的 GitHub Fork 上的 `main` 分支，在本地对应的远程跟踪引用。

---

```
upstream/main
```

表示：

> 原作者仓库的 `main` 分支，在本地对应的远程跟踪引用。

所以可以画成：

```
原作者 GitHub
upstream/main
      │
      │
      ▼
我的本地仓库
main
      │
      │ push
      ▼
我的 GitHub
origin/main
```

---

# 5. Branch 本质是什么？

以前很容易把 branch 想成：

> “复制了一整份项目代码。”

实际上更准确的理解是：

> **branch 本质上只是一个指向某个 commit 的可移动指针。**

例如：

```
A → B → C
        ↑
       main
```

`main` 本质上只是指向：

```
C
```

如果继续提交：

```
A → B → C → D
            ↑
           main
```

`main` 只是从 C 移到了 D。

理解这一点以后：

- `reset`
    
- `rebase`
    
- `force push`
    
- branch
    

都会好理解很多。

---

# 6. Commit 是什么？

Commit 可以理解成：

> **给当前项目状态拍一个 Git 快照。**

例如本次实际有这些提交：

```
Improve classroom WebSocket listener stability

Avoid answering the same lesson problem after reconnect

Keep WebSocket callbacks responsive and reduce listener logs
```

每个 commit 都有自己的 SHA，例如：

```
1473d686...
353c286e...
4acfaf81...
```

SHA 可以理解为这个 commit 的唯一身份标识。

---

# 7. commit 和 push 的区别

这个非常容易混。

## commit

```
git commit
```

只是：

> 把当前改动保存进**本地 Git 历史**。

不会自动传到 GitHub。

---

## push

```
git push
```

才是：

> 把本地 commit 上传到远程 GitHub 仓库。

所以：

```
修改代码
↓
commit
↓
本地 Git 有了新版本
↓
push
↓
GitHub 才看到这些版本
```

---

# 8. Pull Request 到底是什么？

Pull Request 并不是：

> “把一份代码文件提交给维护者。”

更准确地说，PR 是：

> **请求维护者把我的某个 branch 相对于他的 branch 多出来的修改合进去。**

本次 PR #4 本质类似：

```
Base：

Chiu-xaH/Fuck-Yangtze-RainClassroom
main


Head：

frewily/Fuck-Yangtze-RainClassroom
codex/clean-listener-pr-20260924
```

意思就是：

> 请比较我的这个分支和你的 main，看看是否愿意把这些改动合进去。

---

# 9. PR 不是提交之后就“定稿”了

这是这次非常重要的实践经验。

PR 会持续跟踪它的源分支。

例如：

```
PR #4
   ↓
跟踪
codex/clean-listener-pr-20260924
```

如果我继续：

```
修改代码
git commit
git push
```

到这个 branch，

那么：

> PR #4 会自动更新。

不需要重新建立一个 PR。

所以真实的 Code Review 流程经常是：

```
提交 PR
↓
维护者 Review
↓
维护者提出修改意见
↓
继续修改 PR 源分支
↓
push
↓
PR 自动更新
↓
再次 Review
↓
Merge
```

---

# 10. 为什么第一次 PR #3 要关闭？

我一开始主要直接在自己的 `main` 上修改。

但是 GitHub Actions 同时还产生了一些：

```
Auto update logs
```

这样的 commit。

因此提交历史类似：

```
upstream/main
│
├─ Auto update logs        ❌
├─ Auto update logs        ❌
├─ WebSocket 修复          ✅
├─ 防止重复答题            ✅
├─ callback 修复           ✅
├─ Auto update logs        ❌
└─ 其他修改
```

PR 并不只看最终代码。

它还会包含：

> **整个 commit 历史和 diff。**

于是 PR #3 变得比较杂。

维护者本来只想审：

```
WebSocket 修复
防止重复答题
callback 修复
```

但实际上还要看到：

```
日志
GitHub Actions 自动提交
其他文件变化
```

因此需要重新整理。

---

# 11. 如何从 upstream/main 创建一个干净分支？

这里有一个以前很容易产生的误解：

> “从原作者 main 创建新分支，是不是在原作者仓库里建分支？”

不是。

真正的意思是：

> **以** `**upstream/main**` **当前指向的 commit 作为起点，在自己的本地仓库创建一个 branch。**

概念上类似：

```
git fetch upstream

git switch -c codex/clean-listener-pr-20260924 upstream/main
```

于是：

```
upstream/main
     │
     A
     │
     └─────────────┐
                   ▼
         我的本地新分支
codex/clean-listener-pr-20260924
```

这个 branch：

> 仍然属于我。

只是它的“出生点”来自：

```
upstream/main
```

然后 push：

```
git push origin codex/clean-listener-pr-20260924
```

它才出现在我的 GitHub Fork 中。

---

# 12. Cherry-pick 是什么？

新分支虽然干净，但是里面还没有之前已经写好的代码。

当然没必要重新手敲。

这时候可以用：

```
git cherry-pick <commit>
```

Cherry-pick 可以理解为：

> **从另一条 Git 历史中挑出某个 commit，把这个 commit 的代码修改重新应用到当前 branch。**

名字也很好理解：

> 🍒 挑樱桃，只拿需要的 commit。

---

例如原来的历史：

```
A
↓
垃圾日志
↓
垃圾日志
↓
C WebSocket 修复
↓
D 防止重复答题
↓
E callback 修复
↓
垃圾日志
```

新分支：

```
A
```

通过 cherry-pick：

```
挑 C
挑 D
挑 E
```

得到：

```
A
↓
C'
↓
D'
↓
E'
```

这样：

```
日志 commit
```

就不会被带进去。

---

# 13. 为什么 cherry-pick 后 SHA 会变？

例如 PR #3 中：

```
16e4f097
Improve classroom WebSocket listener stability
```

PR #4 中变成：

```
1473d686
Improve classroom WebSocket listener stability
```

看起来：

```
commit message 一样
代码修改一样
```

为什么 SHA 不一样？

因为 Git commit 的身份不只取决于代码。

还与：

- parent commit
    
- commit metadata
    
- 时间
    
- 作者等
    

有关。

原来：

```
垃圾 commit
↓
16e4f097
```

重新 cherry-pick 后：

```
upstream/main
↓
1473d686
```

父 commit 不同，

所以 SHA 就不同。

---

# 14. 为什么 PR #4 比 PR #3 更专业？

PR #3：

```
WebSocket
+ 定时配置
+ 日志
+ Actions
+ README
+ 其他修改
```

PR #4 最后：

```
WebSocket 稳定性
+ 防止重复答题
+ 对应测试
```

优秀的 PR 通常应该做到：

```
一个 PR
≈
一个明确目的
+
相关代码
+
相关测试
+
尽量少的无关修改
```

即：

> **PR scope 越清晰，维护者越容易 Review。**

---

# 15. Code Review 后发生了什么？

PR #4 提交之后，维护者回复：

> 辛苦简单缩小一下对 yml 和 readme 的改动，去掉和本次需求无关的改动，其他没什么问题~

还分别指出：

```
yml 可以仅改动本次需求涉及的地方
README 可以仅改动本次需求涉及的地方
```

意思不是代码本身有严重问题。

而是：

> PR 的 scope 还是稍微太大。

---

# 16. 当时 PR #4 的历史是什么样？

当时大概是：

```
upstream/main
│
C1 WebSocket 修复
│
C2 防止重复答题
│
C3 callback 修复
│
C4 Add configurable weekly listening windows
│
C5 Stop publishing personal attendance logs
```

其中：

```
C1 ✅
C2 ✅
C3 ✅
```

属于本次 WebSocket 修复。

而：

```
C4 ❌
C5 ❌
```

主要涉及：

- LISTEN_WINDOWS
    
- README 大量修改
    
- GitHub Actions 改动
    
- log.json
    
- .gitignore
    
- 日志隐私
    

这些并不是这个 PR 最核心的问题。

---

# 17. 为什么这时候可以直接 reset？

刚好：

```
不需要的 commit
```

都连续出现在最后。

所以不需要复杂重构。

只需要：

> 把 branch 指针退回 C3。

原来：

```
A → C1 → C2 → C3 → C4 → C5
                         ↑
                        HEAD
```

执行概念上的：

```
git reset --hard C3
```

以后：

```
A → C1 → C2 → C3
              ↑
             HEAD
```

C4、C5 不再属于当前 branch。

同时工作区代码也恢复成：

> C3 当时的项目状态。

---

# 18. `git reset --hard` 应该怎么理解？

`reset --hard` 可以理解为：

> **把当前 branch 指针和本地文件一起恢复到指定 commit 的状态。**

例如：

```
C1
↓
C2
↓
C3
↓
C4
↓
C5
↑
main
```

执行：

```
git reset --hard C3
```

以后：

```
C1
↓
C2
↓
C3
↑
main
```

代码也恢复成 C3 时的内容。

所以：

```
C4 修改的 README
C5 修改的 log.json
```

都会从当前 branch 消失。

---

# 19. 为什么普通 push 不行？

问题在于：

本地已经变成：

```
A → C1 → C2 → C3
```

但是 GitHub 远程 branch 还是：

```
A → C1 → C2 → C3 → C4 → C5
```

如果执行：

```
git push
```

Git 会发现：

> 你不是往历史后面增加 commit，而是想把 C4 和 C5 删掉。

于是通常会拒绝：

```
non-fast-forward
```

Git 默认不允许随便重写别人已经看到的远程历史。

---

# 20. Force Push 是什么？

这时候需要：

```
git push --force
```

或者更安全的：

```
git push --force-with-lease
```

意思就是：

> **强制让远程 branch 指向我现在本地 branch 指向的 commit。**

之前远程：

```
A → C1 → C2 → C3 → C4 → C5
                         ↑
                       remote
```

本地：

```
A → C1 → C2 → C3
              ↑
             local
```

force push 后：

```
A → C1 → C2 → C3
              ↑
        local + remote
```

也就是：

```
C4
C5
```

从 PR 所跟踪的 branch 历史中消失。

---

# 21. 为什么 force push 后 PR 还能继续存在？

因为 PR 并不是绑定某一组固定 commit。

PR 绑定的是：

```
Base branch
+
Head branch
```

例如 PR #4：

```
Base：
upstream/main

Head：
frewily/codex/clean-listener-pr-20260924
```

之前 Head 指向：

```
C5
```

所以 PR 展示：

```
C1
C2
C3
C4
C5
```

force push 后 Head 改为指向：

```
C3
```

GitHub 自动重新比较：

```
upstream/main
VS
C3
```

于是 PR 自动变成：

```
C1
C2
C3
```

不需要重新创建 PR。

---

# 22. 这次 force push 最终产生了什么效果？

最后 PR #4 只剩：

```
.github/workflows/python-app.yml
function/listening_socket.py
tests/test_listening_socket.py
```

其中 yml 最后只改了一行：

```
- run: python start.py
+ run: python -u start.py
```

`-u` 表示 Python 使用 unbuffered 输出。

主要作用：

> GitHub Actions 日志能更及时输出。

这与：

- WebSocket 断开
    
- 重连
    
- close code
    
- 错误信息
    

的排查直接相关，

所以保留。

而：

```
README.md
```

最后完全退出 PR。

这就是维护者所谓：

> “缩小改动范围。”

---

# 23. reset、cherry-pick、rebase 分别适合什么？

## reset

适合：

```
C1 ✅
C2 ✅
C3 ✅
C4 ❌
C5 ❌
```

不想要的 commit 全在末尾。

直接：

```
回到 C3
```

最简单。

---

## cherry-pick

适合：

```
C1 ❌
C2 ✅
C3 ❌
C4 ✅
C5 ✅
```

想从复杂历史中：

> 挑几个 commit 搬到另一条干净 branch。

例如：

```
新 branch
↓
cherry-pick C2
cherry-pick C4
cherry-pick C5
```

---

## interactive rebase

适合更复杂的历史整理：

```
C1 ✅
C2 ❌
C3 ✅
C4 ❌
C5 ✅
```

希望在原 branch 上：

- 删除 commit
    
- 合并 commit
    
- 修改顺序
    
- 修改 commit message
    

等。

---

# 24. 为什么 `--force-with-lease` 通常比 `--force` 更安全？

`--force` 基本是在说：

> 不管远端发生过什么，都以我本地为准。

而：

```
git push --force-with-lease
```

更像：

> 如果远端还是我认为的那个版本，就允许覆盖；  
> 如果别人已经偷偷推了新的 commit，则拒绝。

所以团队协作里通常优先：

```
git push --force-with-lease
```

而不是裸：

```
git push --force
```

---

# 25. 本次完整 Git 图

可以把整次经历抽象成：

```
                    原作者
               upstream/main
                     │
                     A
                     │
        ┌────────────┴─────────────┐
        │                          │
        │                          │
我的旧 main                  干净 PR branch
        │                          │
   Auto logs                      C1'
        │                          │
   Auto logs                      C2'
        │                          │
      C1                          C3'
        │                          │
      C2                          C4'
        │                          │
      C3                          C5'
        │                          │
   Auto logs                      │
        │                          │
        ▼                          ▼
      PR #3                      PR #4
      关闭                        │
                                  │ Review
                                  ▼
                           “删掉无关改动”
                                  │
                             reset 到 C3'
                                  │
                            force push
                                  │
                                  ▼
                              C1' C2' C3'
                                  │
                                Merge
                                  │
                                  ▼
                           upstream/main
```

---

# 26. 最值得记住的几个认知

## ① Git 的核心不是文件，而是历史

很多 Git 操作看起来是在：

> 改文件。

实际上更深层是在：

> 修改 commit 图，以及 branch 指向哪个 commit。

---

## ② Branch 不是项目副本

Branch 更准确地说是：

> 指向某个 commit 的可移动指针。

---

## ③ PR 不是固定代码包

PR 是：

> 持续比较 Head branch 和 Base branch。

因此：

```
Head branch 变化
↓
PR 自动变化
```

---

## ④ Commit 历史本身也是代码质量的一部分

代码功能正确不代表 PR 就优秀。

还需要：

```
scope 清晰
commit 干净
没有临时文件
没有日志
没有无关 README 修改
没有顺手重构
```

---

## ⑤ 一个 PR 最好只解决一件事

例如这次最后变成：

```
WebSocket 稳定性
+
避免重复答题
+
对应测试
```

维护者就很容易判断：

> 这几个修改是不是应该进入 main。

---

# 27. 本次几个典型命令的“人话解释”

```
git fetch upstream
```

> 看看原作者仓库现在更新到哪里了。

---

```
git switch -c clean upstream/main
```

> 从原作者当前 main 的状态，建立一个属于我的新 branch。

---

```
git cherry-pick <commit>
```

> 把另一个地方这个 commit 的代码修改搬到我当前 branch。

---

```
git reset --hard <commit>
```

> 当前 branch 走远了，直接恢复到指定 commit，当时后面的修改全不要。

---

```
git push origin clean
```

> 把我的本地 clean branch 上传到我的 GitHub Fork。

---

```
git push --force-with-lease
```

> 我修改了 Git 历史，需要让远端 branch 强制改成现在这条历史，但先确保别人没有偷偷更新它。

---

# 28. 我的几个疑问与答案

## Q1：从 upstream/main 拉新 branch，是不是在原作者仓库里创建 branch？

不是。

是在：

```
我的本地 Git 仓库
```

中，

以：

```
upstream/main
```

作为起点创建一个属于自己的 branch。

---

## Q2：新 branch 怎么获得以前已经写好的代码？重新写一遍吗？

不需要。

可以通过：

```
cherry-pick
```

直接把原来有用 commit 的修改搬过来。

---

## Q3：为什么 cherry-pick 后 commit SHA 变了？

因为：

> commit 的 parent 等历史信息发生了变化。

Git commit 身份不仅取决于代码内容。

---

## Q4：PR 提交后还能改吗？

当然可以。

只需要继续修改：

```
PR 的 Head branch
```

再 push。

PR 自动更新。

---

## Q5：为什么后来要 force push？

因为已经不是：

> 在历史后面增加 commit。

而是：

> 删除 / 重写已有历史。

普通 push 不允许这么做。

所以需要 force push。

---

## Q6：这次是不是相当于恢复以前的快照，再覆盖 PR？

对。

当时：

```
C1
C2
C3
C4
C5
```

发现：

```
C4、C5 不应该出现在 PR
```

于是 branch 回到：

```
C3
```

然后 force push。

PR 自动变成只包含：

```
C1
C2
C3
```

---

# 29. 最终总结

这次开源贡献真正学到的并不是：

```
git 命令怎么背
```

而是：

```
Fork
↓
Clone
↓
Branch
↓
Commit
↓
Push
↓
Pull Request
↓
Code Review
↓
整理 Git 历史
↓
Force Push
↓
Merge
```

以及更核心的一层：

> **Git 管理的不是“某一份最终代码”，而是一条代码演化历史。**

AI 以后完全可以帮我：

- 创建 branch
    
- commit
    
- cherry-pick
    
- rebase
    
- reset
    
- push
    
- 创建 PR
    

但至少我需要知道：

> **AI 此刻是在增加历史、搬运历史、删除历史，还是重写历史。**

这样即使大量操作交给 AI，也不会变成：

> “命令跑完了，但我完全不知道自己的仓库发生了什么。”

这才是学习 Git 最有价值的地方。