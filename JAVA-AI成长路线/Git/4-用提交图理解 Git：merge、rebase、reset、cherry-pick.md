# 用提交图理解 Git：merge、rebase、reset、cherry-pick

> 这篇笔记建立在一个核心认识上：
> 
> **Git 的本质不是管理文件，而是管理 commit 组成的历史图。**
> 
> 一旦能看懂 commit 图，`merge`、`rebase`、`reset`、`cherry-pick` 就不再是几个孤立命令，而只是对“提交历史”的不同操作。

---

# 1. 先建立 Git 最核心的模型

假设现在有三个 commit：

```
A → B → C
        ↑
       main
```

这里：

```
A
B
C
```

都是 commit。

而：

```
main
```

只是一个指向 C 的 branch 指针。

所以：

> branch 并不是一整份代码副本。

而更接近：

> **一个会移动的标签 / 指针。**

---

# 2. HEAD 又是什么？

除了 branch，还有一个经常看到的东西：

```
HEAD
```

HEAD 可以理解为：

> **我当前正在操作哪个位置。**

通常 HEAD 指向当前 branch。

例如：

```
A → B → C
        ↑
      main
        ↑
      HEAD
```

表示：

> 我现在位于 `main` branch。

如果再 commit 一个 D：

```
A → B → C → D
            ↑
          main
            ↑
          HEAD
```

Git 会：

1. 创建 D；
    
2. 让 D 的 parent 指向 C；
    
3. 把 main 指针移动到 D。
    

---

# 3. 为什么 Git 是“图”而不是单纯链表？

如果一直只在一个 branch 开发：

```
A → B → C → D
```

看起来像链表。

但只要出现多个 branch：

```
A → B → C
         \
          D → E
```

就出现分叉了。

例如：

```
A → B → C
        ↑
       main
         \
          D → E
              ↑
            feature
```

因此 Git 的提交结构更准确地说是：

> **有向无环图 DAG（Directed Acyclic Graph）**

每个 commit 都记录：

> 我的 parent commit 是谁。

---

# 4. 创建 branch 到底发生了什么？

假设：

```
A → B → C
        ↑
       main
```

执行：

```
git switch -c feature
```

并不会复制一套完整代码。

只是多创建一个指针：

```
A → B → C
        ↑
       main
        ↑
      feature
        ↑
       HEAD
```

这时候：

```
main
feature
```

都指向 C。

然后在 feature 上提交：

```
A → B → C → D
        ↑       ↑
       main   feature
```

再提交：

```
A → B → C → D → E
        ↑           ↑
       main       feature
```

于是 branch 就“分叉”了。

---

# 5. switch / checkout 本质是在干什么？

例如：

```
git switch main
```

其实主要做两件事：

1. HEAD 切到 `main`；
    
2. 工作区恢复成 `main` 当前 commit 对应的文件状态。
    

原来：

```
A → B → C → D → E
        ↑           ↑
       main       feature
                    ↑
                   HEAD
```

切回 main：

```
A → B → C → D → E
        ↑           ↑
       main       feature
        ↑
       HEAD
```

工作目录也会跟着恢复到 C 的状态。

---

# 6. merge 是什么？

假设开发过程：

```
A → B → C
         \
          D → E
```

其中：

```
main = C
feature = E
```

现在希望把 feature 合回 main。

---

## 情况一：Fast-forward merge

如果 main 在 feature 开发期间没有新增 commit：

```
A → B → C → D → E
        ↑           ↑
       main       feature
```

此时执行：

```
git switch main
git merge feature
```

Git 发现：

> E 本来就是 C 的后代。

那就没必要创建新的 merge commit。

只需要：

```
main 指针从 C 移到 E
```

于是：

```
A → B → C → D → E
                    ↑
               main / feature
```

这叫：

> **Fast-forward Merge**

即：

> 快进合并。

本质就是：

> “你本来就在我的历史后面，我直接把指针往前移动。”

---

# 7. 真正的 Merge Commit

如果 main 和 feature 都继续开发：

```
          D → E
         /
A → B → C
         \
          F → G
```

假设：

```
feature = E
main = G
```

这时候两条历史已经真正分叉。

执行：

```
git merge feature
```

Git 会创建一个新的 commit：

```
          D → E
         /     \
A → B → C       M
         \     /
          F → G
```

其中：

```
M
```

就是 Merge Commit。

它比较特殊：

> 普通 commit 通常只有一个 parent。

而：

```
M
```

有两个 parent：

```
E
G
```

这相当于记录：

> “从这里开始，这两条历史重新汇合了。”

---

# 8. merge 的特点

Merge 最大特点：

> **保留原始历史结构。**

例如：

```
          D → E
         /     \
A → B → C       M
         \     /
          F → G
```

你能清楚看到：

- feature 什么时候分出去；
    
- main 后来做了什么；
    
- 最后什么时候合回来。
    

优点：

> 历史真实、不会重写旧 commit。

缺点：

> branch 很多时提交图可能比较乱。

---

# 9. rebase 是什么？

还是这个情况：

```
          D → E
         /
A → B → C
         \
          F → G
```

如果不 merge，而是在 feature 上执行：

```
git rebase main
```

Git 会做的事情更像：

> “把 D、E 的修改拿出来，然后重新放到 G 后面。”

结果：

```
A → B → C → F → G → D' → E'
```

原来的：

```
D
E
```

变成：

```
D'
E'
```

---

# 10. 为什么 rebase 后 SHA 会变化？

因为原来的 D：

```
parent = C
```

而 rebase 后的 D'：

```
parent = G
```

parent 改了。

所以：

```
D ≠ D'
```

即使代码改动完全一样，

commit SHA 也会变。

这和之前真实 PR 中的 cherry-pick 很像。

---

# 11. merge 和 rebase 的核心区别

Merge：

```
          D → E
         /     \
A → B → C       M
         \     /
          F → G
```

Rebase：

```
A → B → C → F → G → D' → E'
```

可以理解成：

## Merge

> “两条历史都保留，最后汇合。”

## Rebase

> “把我的历史重新接到最新 main 后面，看起来好像我是后来才开始开发的一样。”

---

# 12. 为什么很多人喜欢 rebase？

因为它可以让历史比较直：

```
A → B → C → D → E → F → G
```

而不是：

```
       D → E
      /     \
A → B       M
      \     /
       F → G
```

特别是在 PR 开发时，常常希望：

> feature branch 看起来是基于最新 main 开发的。

于是：

```
git fetch upstream
git rebase upstream/main
```

很常见。

---

# 13. rebase 为什么属于“重写历史”？

因为：

```
D → E
```

会变成：

```
D' → E'
```

原 commit 被重新生成。

所以 SHA 变化。

这意味着：

> 如果这些 commit 已经 push 到远端，

rebase 以后普通 push 很可能失败。

通常需要：

```
git push --force-with-lease
```

因此：

> **不要轻易 rebase 别人正在共同使用的公共 branch。**

---

# 14. cherry-pick 与 rebase 有什么关系？

它们底层思想其实挺像。

比如：

```
A → B → C

X → D → E
```

在 C 上执行：

```
git cherry-pick D
```

得到：

```
A → B → C → D'
```

也就是：

> 把 D 的修改重新应用到 C 后面。

如果继续：

```
git cherry-pick E
```

得到：

```
A → B → C → D' → E'
```

是不是很像 rebase？

没错。

---

# 15. rebase 可以理解成“批量 cherry-pick”

粗略理解：

```
rebase
≈
自动把一串 commit 逐个 cherry-pick 到新的 base 上
```

例如：

```
D → E → F
```

rebase 到 main：

```
main → D' → E' → F'
```

不过 rebase 还有更多历史处理能力，因此不能完全等同。

但作为初学理解：

> **rebase ≈ 批量搬迁 commit**

非常实用。

---

# 16. cherry-pick 最适合什么场景？

例如：

```
A → B → C → D → E → F
```

其中：

```
C ❌
D ✅
E ❌
F ✅
```

我只想要：

```
D
F
```

这时候可以新开 clean branch：

```
A → B
```

然后：

```
git cherry-pick D
git cherry-pick F
```

得到：

```
A → B → D' → F'
```

这正是之前清理 PR 历史时用到的思想。

---

# 17. reset 到底是什么？

假设：

```
A → B → C → D → E
                ↑
               main
```

如果执行：

```
git reset C
```

核心动作其实是：

> **把 main 指针移动回 C。**

于是：

```
A → B → C
        ↑
       main

D → E
```

D、E 并不是瞬间从硬盘永久消失。

只是：

> main 不再指向它们了。

---

# 18. reset 有三种常见模式

## `--soft`

```
git reset --soft C
```

branch 回到 C，

但 D、E 的改动仍然保留在：

> staged area。

可以理解：

> commit 撤销了，但文件修改还准备着重新提交。

---

## `--mixed`

默认：

```
git reset C
```

相当于：

```
git reset --mixed C
```

branch 回 C，

D、E 修改还在工作区，

但不再 staged。

---

## `--hard`

```
git reset --hard C
```

这是最彻底的：

```
branch
staging area
working tree
```

全部回到 C 的状态。

也就是：

> D、E 后面的工作区修改也不要了。

---

# 19. 为什么之前 PR Review 后适合 reset --hard？

当时 PR 分支类似：

```
A
↓
C1 ✅
↓
C2 ✅
↓
C3 ✅
↓
C4 ❌
↓
C5 ❌
```

学长说：

> C4、C5 这些无关改动去掉。

这种情况非常适合：

```
git reset --hard C3
```

因为：

> 不需要的 commit 恰好全部在最末尾。

得到：

```
A → C1 → C2 → C3
```

干净利落。

---

# 20. 如果不需要的 commit 在中间怎么办？

比如：

```
A
↓
C1 ✅
↓
C2 ❌
↓
C3 ✅
↓
C4 ❌
↓
C5 ✅
```

这时候不能简单：

```
git reset --hard C1
```

因为这样：

```
C3
C5
```

也没了。

这时候通常考虑：

```
interactive rebase
```

或者：

```
新 branch + cherry-pick
```

---

# 21. interactive rebase 是什么？

例如：

```
git rebase -i HEAD~5
```

Git 会让你看到类似：

```
pick C1
pick C2
pick C3
pick C4
pick C5
```

可以修改成：

```
pick C1
drop C2
pick C3
drop C4
pick C5
```

最后：

```
A → C1' → C3' → C5'
```

还可以：

```
reword
squash
fixup
edit
drop
```

分别用于：

- 修改 commit message；
    
- 合并 commit；
    
- 合并但丢弃 message；
    
- 暂停编辑；
    
- 删除 commit。
    

---

# 22. squash 是什么？

假设开发过程中提交得很碎：

```
A
↓
fix websocket
↓
oops fix typo
↓
fix test
↓
really fix websocket
```

这些其实都属于一个功能。

可以 squash 成：

```
A
↓
Fix WebSocket reconnect handling
```

让 PR 历史更清晰。

这也是大型开源项目经常关注的东西：

> commit 应该具有逻辑完整性。

---

# 23. revert 又是什么？

这是一个和 reset 很容易混淆的命令。

假设：

```
A → B → C → D
```

发现 D 是错误提交。

---

## reset

```
git reset --hard C
```

变成：

```
A → B → C
```

相当于：

> 修改历史，让 D 不再属于 branch。

---

## revert

```
git revert D
```

变成：

```
A → B → C → D → E
```

其中：

```
E
```

专门做：

> 把 D 的修改反向撤销。

历史仍然保留：

```
D 做错了
E 把 D 撤销了
```

---

# 24. reset 和 revert 怎么选？

一个很好记的原则：

## 私人 branch / 尚未共享的历史

可以考虑：

```
reset
rebase
```

因为可以重写历史。

---

## 公共 main / 已经多人使用

一般更适合：

```
revert
```

因为不需要篡改已有历史。

例如已经上线：

```
A → B → C → BugCommit
```

这时候最好：

```
A → B → C → BugCommit → RevertBug
```

而不是直接假装 BugCommit 从没存在过。

---

# 25. force push 到底为什么危险？

假设远端：

```
A → B → C
```

你本地也是：

```
A → B → C
```

但是队友偷偷 push：

```
A → B → C → D
```

你没 fetch，所以本地还不知道 D。

如果你本地 reset：

```
A → B
```

然后：

```
git push --force
```

远端会变成：

```
A → B
```

队友的：

```
C
D
```

可能都被覆盖掉。

所以危险。

---

# 26. 为什么推荐 `--force-with-lease`？

```
git push --force-with-lease
```

它会先检查：

> “远端是不是还处于我上次看到的状态？”

如果别人已经更新：

```
remote:
A → B → C → D
```

但我以为还是：

```
A → B → C
```

它会拒绝 force push。

因此：

```
--force
```

≈

> 不管别人干了什么，覆盖。

而：

```
--force-with-lease
```

≈

> 如果没人背着我更新，再覆盖。

所以通常后者更安全。

---

# 27. merge、rebase、cherry-pick、reset 一张表理解

|操作|核心动作|是否产生新 commit|是否可能重写历史|
|---|---|---|---|
|`merge`|把两条历史合起来|可能|否|
|`rebase`|把一串 commit 搬到新的 base|是|是|
|`cherry-pick`|单独搬一个或几个 commit|是|通常是|
|`reset`|移动当前 branch 指针|否|是|
|`revert`|新增一个反向撤销 commit|是|否|

---

# 28. 用一句话理解每个命令

## merge

> 两条路都保留，在终点汇合。

---

## rebase

> 把我的整段路搬到你的最新路后面。

---

## cherry-pick

> 从别的历史里挑几个 commit 搬过来。

---

## reset

> 把当前 branch 指针拨回以前。

---

## revert

> 不删旧历史，再新增一个 commit 把以前的改动抵消。

---

# 29. 用这次真实 PR 来对应

这次实际基本经历了：

## 第一阶段：main 比较乱

```
upstream/main
│
├─ Auto logs
├─ Auto logs
├─ WebSocket fix
├─ duplicate answer fix
├─ callback fix
└─ Auto logs
```

---

## 第二阶段：建立 clean branch

从：

```
upstream/main
```

重新开始：

```
A
```

---

## 第三阶段：cherry-pick

把需要的几个 commit 搬过来：

```
A
↓
C1'
↓
C2'
↓
C3'
```

---

## 第四阶段：后来又加了额外功能

```
A
↓
C1'
↓
C2'
↓
C3'
↓
C4'
↓
C5'
```

---

## 第五阶段：Reviewer 要求缩小范围

发现：

```
C4'
C5'
```

不属于本次 PR。

于是：

```
reset --hard C3'
```

---

## 第六阶段：远端历史不同步

远端：

```
C3' → C4' → C5'
```

本地：

```
C3'
```

普通 push：

```
拒绝
```

于是：

```
force-with-lease
```

---

## 第七阶段：PR 自动刷新

PR Head 从：

```
C5'
```

变成：

```
C3'
```

于是 PR 自动只显示：

```
C1'
C2'
C3'
```

---

# 30. AI 帮我操作 Git 时，应该关注什么？

以后 AI 说：

```
“我准备 cherry-pick 三个提交”
```

应该理解为：

> 从另一条历史中挑三个 commit 的修改搬过来。

---

AI 说：

```
“我要 rebase 到 upstream/main”
```

应该理解：

> 把当前 branch 的 commit 重新接到最新 upstream/main 后面，因此 SHA 可能全部变化。

---

AI 说：

```
“我要 reset 到某 commit”
```

应该立刻意识到：

> branch 指针要往回移动，后面的 commit 可能不再属于这个 branch。

---

AI 说：

```
“需要 force push”
```

就应该警觉：

> Git 历史被重写了。

这时至少确认：

```
这是我自己的 feature branch 吗？
有没有其他人在这个 branch 上工作？
为什么普通 push 不行？
到底哪些 commit 会被远端覆盖？
```

---

# 31. 一个很好用的安全习惯

AI 要执行这些操作时：

```
reset --hard
rebase
push --force
```

最好让它先展示：

```
git status
git log --oneline --graph --decorate --all
```

因为：

```
git status
```

可以看：

> 当前工作区有没有还没保存的改动。

而：

```
git log --oneline --graph --decorate --all
```

可以看：

> branch 到底指向哪里。

例如：

```
* 4acfaf8 (HEAD -> clean, origin/clean) callback fix
* 353c286 duplicate answer fix
* 1473d68 websocket fix
| * abc123 (main, origin/main) ...
|/
* 9829b32 (upstream/main)
```

这类图比单纯听 AI 说：

> “已经整理好了。”

更值得信任。

---

# 32. 我的 Git 心智模型

以后不应该只问：

> “这条 Git 命令有什么作用？”

更应该问：

> **“执行以后，commit 图会从什么样变成什么样？”**

例如：

```
merge：
图会汇合

rebase：
commit 会搬家

cherry-pick：
挑 commit 复制修改

reset：
branch 指针回退

force push：
让远端 branch 接受本地被重写后的历史
```

只要脑子里能画出：

```
执行前
↓
执行后
```

就算不记得具体命令，也真正理解 Git 了。

---

# 33. 最终总结

Git 中最值得理解的几个对象：

```
Commit
= 一个历史节点

Branch
= 指向 commit 的可移动指针

HEAD
= 我当前所在的位置

Remote
= 远程仓库

origin
= 通常是自己的远程仓库

upstream
= 通常是原始项目仓库

Pull Request
= 比较两个 branch 并请求合并
```

最值得理解的几个动作：

```
merge
= 汇合历史

rebase
= 搬迁历史

cherry-pick
= 挑选历史

reset
= 移动 branch 指针

revert
= 用新历史撤销旧历史

force push
= 用本地被重写的历史覆盖远端 branch
```

最后最重要的一句话：

> **Git 的很多“高级操作”，本质上都只是在操作 commit 图，以及改变 branch 指针指向哪里。**

理解 commit 图，比背几十条 Git 命令重要得多。