---
name: lemon-commit-code
description: 代码提交与推送技能。审查变更代码后生成规范提交信息并推送到所有远程仓库。使用流程：1) 使用 git status/diff 查看变更 2) 审查代码质量 3) 生成提交信息 4) 提交并推送到所有远程仓库。支持 Conventional Commits 规范。
---

# Lemon Commit Code

## 触发场景

当用户请求：
- 提交并推送代码到仓库
- 生成规范的 commit message
- 审查变更后提交代码

## 工作流程

### 1. 查看变更状态

使用 Bash 工具执行：

```bash
# 查看工作区状态
git status

# 查看变更摘要
git diff --stat

# 查看详细变更
git diff
```

### 2. 代码审查

按以下维度检查变更代码：

| 维度 | 检查项 |
|------|--------|
| **业务逻辑** | 业务流程是否正确、边界条件处理 |
| **安全性** | SQL注入、XSS、权限校验 |
| **性能** | N+1查询、大对象、循环操作 |
| **规范** | 命名、注释、代码结构 |
| **测试** | 关键逻辑是否有测试覆盖 |

**审查结果输出格式**：

```markdown
## 代码审查报告

### 审查文件
- `src/xxx.java`

### 问题列表
| 严重程度 | 问题描述 | 位置 |
|---------|---------|------|
| 🔴 严重 | ... | ... |
| 🟡 警告 | ... | ... |

### 审查结论
✅ 可以提交 / ⚠️ 需修复后提交
```

### 3. 生成提交信息

基于变更内容生成符合 Conventional Commits 规范的提交信息：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**常用 type**：
- `feat`: 新功能
- `fix`: Bug修复
- `refactor`: 重构
- `docs`: 文档更新
- `style`: 代码格式
- `test`: 测试相关
- `chore`: 构建/工具

### 4. 提交代码

```bash
# 暂存变更文件（包括新增、修改、删除）
git add -A

# 或者只暂存特定文件
git add <file1> <file2> ...

# 提交（不包含 Claude 署名信息）
git commit -m "$(cat <<'EOF'
<generated message>
EOF
)"
```

**重要提示**：
- **不要添加 Co-authored-by 署名**：提交信息中不应包含 `Co-authored-by: Claude <noreply@anthropic.com>` 等 AI 署名信息
- 保持提交信息简洁，只包含实际的变更描述

**注意**：`git add -A` 会暂存所有变更，包括：
- 新增文件 (untracked files)
- 修改文件 (modified files)
- 删除文件 (deleted files)

### 5. 推送到所有远程仓库（⚠️ 强制执行）

**⚠️ 强制要求：必须推送到所有远程仓库，不得遗漏任何仓库！**

```bash
# 步骤1: 查看所有远程仓库
git remote

# 步骤2: 获取当前分支名
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# 步骤3: 推送到所有远程仓库（三选一）

# 方法1: Bash 循环推送（推荐 - 适用于 Git Bash/Linux）
for remote in $(git remote); do git push $remote $CURRENT_BRANCH; done

# 方法2: Windows PowerShell 版本
git remote | ForEach-Object { git push $_ $env:CURRENT_BRANCH }

# 方法3: 逐个推送（最明确，不会遗漏）
git push origin $CURRENT_BRANCH
git push github $CURRENT_BRANCH
git push gitee $CURRENT_BRANCH
# ... 继续推送所有其他仓库
```

**执行后验证**：
- 必须确认每个仓库都推送成功
- 如有失败必须重试直到全部成功
- 输出推送结果表格，显示所有仓库状态

## 注意事项

1. **必须审查**: 提交前必须先进行代码审查，发现问题需提示用户
2. **⚠️ 推送到所有仓库**: 必须推送到所有远程仓库（origin、github、gitee 等），不能只推送到单个仓库，这是强制要求
3. **不添加 AI 署名**: 提交信息中不要添加 `Co-authored-by: Claude` 等 AI 署名信息
4. **包含新文件**: 使用 `git add -A` 会包含所有新增文件，需确认没有敏感或不需要提交的文件
5. **用户确认**: 重大变更或复杂功能建议用户确认后再提交
6. **分支检查**: 确认当前分支正确，避免在主分支直接提交
7. **提交信息**: 必须包含有意义的描述，避免模糊信息
8. **安全提示**: 敏感信息（密钥、密码）不能提交

## 示例

用户输入：
```
帮我提交代码
```

操作流程：
1. `git status` → 查看变更文件（包括新增和修改）
2. `git diff` → 审查变更内容
3. 如有新增文件，确认是否需要提交
4. 输出版本审查报告
5. 生成提交信息：
   ```
   feat(user): 新增用户登录功能

   - 支持用户名密码登录
   - 添加记住密码功能
   - 优化登录错误提示
   ```
6. `git add -A` → `git commit` → **推送到所有远程仓库**
   ```bash
   git remote                    # 查看所有远程仓库
   git push origin master        # 推送到 origin
   git push github master        # 推送到 github
   # 必须推送所有仓库，不能遗漏
   ```
