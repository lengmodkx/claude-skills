---
name: lemon-commit-code
description: 智能代码提交与推送技能。自动审查所有变更代码、进行质量检查、优化建议、生成规范提交信息并推送到所有远程仓库。完整流程：查看变更 → 代码审查 → 强制安全检查 → 问题修复建议 → 生成提交信息 → 提交并推送到所有远程仓库。支持 Conventional Commits 规范，支持多仓库同步推送。
---

# Lemon Commit Code

## 触发场景

当用户请求：
- 提交并推送代码到所有远程仓库
- 生成规范的 commit message
- 审查变更后提交代码
- 多仓库同步推送（GitHub + Gitee 等）
- "提交"、"推送"、"commit" 等相关关键词

## 核心流程

### 阶段一：变更分析

#### 1.1 查看当前状态

\`\`\`bash
# 查看工作区状态
git status

# 查看当前分支
git branch --show-current

# 查看最近的提交记录
git log --oneline -5
\`\`\`

#### 1.2 自动添加所有变更到暂存区

**在开始审查之前，先添加所有未提交的文件**

\`\`\`bash
# 自动添加所有变更（包括已修改、已删除和未跟踪的文件）
git add -A
\`\`\`

**说明**:
- 自动暂存所有未提交的文件
- 包括：已修改、已删除、未跟踪的新文件
- 确保所有变更都纳入代码审查和安全检查范围

#### 1.4 查看变更内容

\`\`\`bash
# 查看所有变更的详细内容
git diff HEAD

# 查看变更统计
git diff --stat HEAD
\`\`\`

---

### 阶段二：自动代码审查

**必须先调用 \`lemon-code-review\` 技能对所有变更代码进行全面审查**

#### 2.1 审查维度

| 维度 | 检查项 | 严重程度 |
|------|--------|----------|
| **业务逻辑** | 业务流程正确性、边界条件、异常处理 | 🔴 |
| **安全性** | SQL注入、XSS、权限校验、敏感数据 | 🔴 |
| **性能** | N+1查询、大对象、循环效率 | 🔴 |
| **规范** | 命名、注释、代码结构、异常处理 | 🟡 |
| **最佳实践** | 设计模式、资源管理、事务范围 | 🟡 |

#### 2.2 审查报告格式

\`\`\`markdown
## 代码审查报告

### 变更文件
- \`path/to/file1.java\` - 新增/修改
- \`path/to/file2.java\` - 修改

### 问题列表

| 严重程度 | 问题描述 | 文件位置 | 建议修复 |
|---------|---------|---------|---------|
| 🔴 严重 | N+1 查询问题 | UserService.java:85 | 使用批量查询 |
| 🟡 警告 | 缺少日志记录 | OrderController.java:42 | 添加 debug 日志 |
| 🟢 提示 | 可优化为 Stream | DataUtil.java:120 | 使用 Stream API |

### 审查结论
📊 代码质量评分: ⭐⭐⭐⭐☆ (4/5)

⚠️ 发现 2 个严重问题，建议修复后再提交
\`\`\`

---

### 阶段三：问题处理

#### 3.1 问题分类

根据审查结果，将问题分为：

- **🔴 必须修复**: 安全漏洞、严重性能问题、业务逻辑错误
- **🟡 建议修复**: 代码规范、小性能优化
- **🟢 可选优化**: 代码风格、小幅改进

#### 3.2 用户确认

**如果发现 🔴 严重问题**：
\`\`\`
⚠️ 发现以下严重问题需要修复：

[列出问题列表]

🔴 严重问题必须修复后才能提交。是否需要我立即修复？
- 选项1: 是，帮我修复
- 选项2: 我手动修复后再提交

**注意：严重安全问题和代码质量问题不允许跳过，必须修复后才能提交**
\`\`\`

**如果只有 🟡/🟢 问题**：
\`\`\`
✅ 代码审查通过，发现以下可优化项：

[列出优化建议]

是否继续提交？
- 选项1: 继续提交
- 选项2: 先优化再提交
\`\`\`

---

### 阶段三B：强制安全检查

**在生成提交信息之前，必须执行以下强制安全检查**

#### 3B.1 敏感信息检测（强制执行）

\`\`\`bash
# 检测暂存区中的敏感信息
echo "🔍 执行敏感信息检测..."

sensitive_files=$(git diff --cached --name-only | grep -E "\.(java|yml|yaml|properties|xml|js|ts|py|go|php|env|config)$")

if [ -n "$sensitive_files" ]; then
    sensitive_patterns=$(git diff --cached $sensitive_files | grep -iE "(password|secret|token|api_key|private_key|access_key|auth_key|credentials|client_secret|jwt_secret)")

    if [ -n "$sensitive_patterns" ]; then
        echo ""
        echo "❌ 检测到可能的敏感信息，提交已终止"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "发现以下敏感内容："
        echo "$sensitive_patterns"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "请执行以下操作后重试："
        echo "  1. 从代码中移除硬编码的敏感信息"
        echo "  2. 使用环境变量或配置文件模板"
        echo "  3. 将敏感文件添加到 .gitignore"
        echo "  4. 如果已提交，使用 git filter-branch 或 BFG Repo-Cleaner 清理历史"
        echo ""
        exit 1
    fi
fi

echo "✅ 敏感信息检测通过"
\`\`\`

#### 3B.2 分支安全检查（强制执行）

\`\`\`bash
echo "🔍 执行分支安全检查..."

current_branch=$(git branch --show-current)
protected_branches=("main" "master")

for protected in "${protected_branches[@]}"; do
    if [ "$current_branch" = "$protected" ]; then
        echo ""
        echo "⚠️  警告：您正在 $protected 分支上操作"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "最佳实践："
        echo "  1. 使用 feature 分支开发"
        echo "  2. 通过 Pull Request/Merge Request 合并"
        echo "  3. 确保 CI/CD 检查通过后再合并"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        read -p "确认要继续在 $protected 分支提交吗？输入 'yes' 继续: " confirm
        if [ "$confirm" != "yes" ]; then
            echo "提交已取消"
            exit 1
        fi
        break
    fi
done

echo "✅ 分支安全检查通过"
\`\`\`

#### 3B.3 禁止提交的文件类型检查（强制执行）

\`\`\`bash
echo "🔍 执行文件类型检查..."

# 检查是否包含禁止提交的文件
forbidden_found=false
staged_files=$(git diff --cached --name-only)

# 检查编译产物
if echo "$staged_files" | grep -qE "\.(class|jar|war|ear|exe|dll|so|dylib)$"; then
    echo "❌ 检测到编译产物文件，不应提交"
    forbidden_found=true
fi

# 检查目录
if echo "$staged_files" | grep -qE "^(target/|build/|node_modules/|\.idea/|\.vscode/|dist/)"; then
    echo "❌ 检测到构建工具目录或 IDE 配置，不应提交"
    forbidden_found=true
fi

# 检查临时文件
if echo "$staged_files" | grep -qE "\.(log|tmp|bak|swp|swo|DS_Store)$"; then
    echo "❌ 检测到临时文件，不应提交"
    forbidden_found=true
fi

# 检查本地配置
if echo "$staged_files" | grep -qE "(local|\.local)\.(properties|yml|yaml|yaml|config|env)$"; then
    echo "❌ 检测到本地配置文件，不应提交"
    forbidden_found=true
fi

if [ "$forbidden_found" = true ]; then
    echo ""
    echo "请从暂存区移除这些文件或将其添加到 .gitignore："
    echo "  git reset HEAD <file>"
    echo ""
    exit 1
fi

echo "✅ 文件类型检查通过"
\`\`\`

**重要：所有安全检查必须全部通过后才能继续下一步**

---

### 阶段四：智能提交信息生成

#### 4.1 分析变更类型

根据变更内容自动识别：

| 变更内容 | Type | Scope 示例 |
|---------|------|-----------|
| 新增接口/功能 | feat | user, order, api |
| 修复 Bug | fix | login, payment |
| 重构代码 | refactor | service, dao |
| 更新文档 | docs | readme, api |
| 代码格式 | style | - |
| 添加测试 | test | unit, integration |
| 构建/工具 | chore | dependency, config |
| 性能优化 | perf | database, cache |

#### 4.2 生成提交信息模板

\`\`\`
<type>(<scope>): <subject>

## 主要变更

- [功能1] 描述
- [功能2] 描述
- [优化1] 描述

## 技术细节

- [技术点1] 说明
- [技术点2] 说明
\`\`\`

---

### 阶段五：提交与推送

#### 5.1 添加文件到暂存区

**重要：自动添加所有未提交的文件**

\`\`\`bash
# 自动添加所有变更（包括已修改、已删除和未跟踪的文件）
git add -A
\`\`\`

**说明**:
- 使用 \`git add -A\` 自动添加所有未提交的文件
- 包括：已修改的文件、已删除的文件、未跟踪的新文件
- 无需手动选择文件，确保所有变更都被提交
- 安全检查会在暂存后执行，如有问题会阻止提交

#### 5.2 执行提交

**重要：提交信息中不得包含任何 AI 工具的署名信息，包括但不限于：**
- ❌ `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
- ❌ `Co-Authored-By: Claude <noreply@anthropic.com>`
- ❌ 任何类似的 AI 工具标识

\`\`\`bash
git commit -m "$(cat <<'EOF'
<生成的提交信息>
EOF
)"
\`\`\`

#### 5.3 推送到所有远程仓库（需用户确认）

\`\`\`bash
# 获取所有远程仓库
remotes=$(git remote)
current_branch=$(git branch --show-current)

if [ -z "$remotes" ]; then
    echo "⚠️  未配置任何远程仓库"
    exit 1
fi

echo "📤 发现以下远程仓库："
echo "$remotes"
echo ""

# 遍历所有远程仓库进行推送
push_success_count=0
push_failed_count=0

for remote in $remotes; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📤 正在推送到远程仓库: $remote"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 检查该远程仓库是否已设置上游
    if git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
        # 已设置上游，直接推送
        if git push $remote $current_branch; then
            echo "✅ 推送到 $remote 成功"
            push_success_count=$((push_success_count + 1))
        else
            echo "❌ 推送到 $remote 失败"
            push_failed_count=$((push_failed_count + 1))
        fi
    else
        # 未设置上游，设置上游并推送
        echo "🔗 首次推送到 $remote，设置上游分支..."
        if git push --set-upstream $remote $current_branch; then
            echo "✅ 推送到 $remote 成功并已设置上游"
            push_success_count=$((push_success_count + 1))
        else
            echo "❌ 推送到 $remote 失败"
            push_failed_count=$((push_failed_count + 1))
        fi
    fi
    echo ""
done

# 输出推送结果汇总
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 推送结果汇总"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 成功: $push_success_count 个远程仓库"
if [ $push_failed_count -gt 0 ]; then
    echo "❌ 失败: $push_failed_count 个远程仓库"
    echo ""
    echo "⚠️  部分远程仓库推送失败，请检查网络连接或仓库配置"
    exit 1
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
\`\`\`

---

## 安全检查清单

### 禁止提交的内容

- ❌ **敏感信息**: 密钥、密码、Token、私钥、API Key
- ❌ **编译产物**: \`target/\`, \`*.class\`, \`*.jar\`, \`node_modules/\`
- ❌ **IDE 配置**: \`.idea/\`, \`.vscode/\`, \`*.iml\`
- ❌ **本地配置**: \`application-local.yml\`, \`local.properties\`
- ❌ **临时文件**: \`*.log\`, \`*.tmp\`, \`.DS_Store\`
- ❌ **测试数据**: \`test_data.sql\`, \`mock_data.json\`

### 敏感信息模式

以下模式会被强制检测并阻止提交：

\`\`\`
password, secret, token, api_key, private_key, access_key,
auth_key, credentials, client_secret, jwt_secret
\`\`\`

---

## 注意事项

### 0. 自动提交原则
- **自动添加所有未提交的文件**：使用 \`git add -A\` 暂存所有变更
- 包括已修改、已删除和未跟踪的新文件
- 无需手动选择文件，确保所有变更都被提交
- 所有文件都会经过代码审查和安全检查，确保安全性

### 1. 审查优先原则
- **必须先审查，后提交**
- 发现严重问题必须提示用户
- **严重问题不允许跳过，必须修复后才能提交**

### 2. 用户确认原则
- 所有未提交的文件会自动添加到暂存区
- 重大变更需要用户确认
- 有争议的代码需要用户决定
- 尊重用户的最终决定（但安全检查不可绕过）

### 3. 分支安全原则
- **强制检查当前分支**
- 在 main/master 分支提交需要用户明确输入 'yes' 确认
- 强烈建议使用 feature 分支开发

### 4. 提交信息质量
- Subject 简洁明了（< 50 字符）
- Body 详细说明变更原因和方式
- 避免使用 "fix"、"update" 等模糊信息
- **禁止在提交信息中包含任何 AI 工具的署名或标识**

### 5. 安全第一原则
- **所有安全检查都是强制的，不可跳过**
- 发现敏感信息必须终止提交流程
- 确保不会将敏感数据泄露到代码仓库

---

## 技能协作

此技能会调用以下技能：

1. **lemon-code-review**: 执行代码审查
2. **lemon-domain**: 确保需求明确（如需要）

---

## 参考资源

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Commitlint](https://commitlint.js.org/)
- [Git 提交规范](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)
