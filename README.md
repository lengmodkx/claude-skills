# Claude Code Skills Collection

这是一个精选的 [Claude Code](https://claude.ai/code) 技能集合，旨在提升开发效率和自动化水平。每个技能都经过精心设计，解决特定的开发和工作场景问题。

## 📋 目录

- [目录结构](#目录结构)
- [技能列表](#技能列表)
- [Agents](#agents)
- [第三方插件](#第三方插件)
- [快速开始](#快速开始)
- [技能详解](#技能详解)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 📁 目录结构

```
claude-skills/
├── README.md                    # 项目说明文档
├── agents/                      # Claude Code 专用 Agents
│   ├── backend-architect.md     # 后端架构专家
│   ├── code-reviewer.md         # 代码审查专家
│   ├── context-manager.md       # 上下文管理专家
│   ├── error-detective.md       # 错误侦探
│   ├── frontend-developer.md    # 前端开发专家
│   ├── fullstack-developer.md   # 全栈开发专家
│   ├── performance-engineer.md  # 性能工程师
│   ├── task-decomposition-expert.md  # 任务分解专家
│   ├── technical-researcher.md  # 技术研究员
│   └── test-engineer.md         # 测试工程师
│
├── third-party/                 # 第三方插件集合
│   └── obsidian-skills/         # Obsidian 技能插件 (来自 kepano/obsidian-skills)
│       ├── obsidian-markdown/   # Obsidian Markdown 编辑
│       ├── obsidian-bases/      # Obsidian Bases 编辑
│       └── json-canvas/         # JSON Canvas 编辑
│
├── artifacts-builder/           # 创建复杂 HTML artifacts (React + Tailwind + shadcn/ui)
├── canvas-design/               # 创建视觉艺术设计 (PNG/PDF)
├── changelog-generator/         # 自动生成 changelog
├── consumption-statistics/      # 消费统计助手
├── docx/                        # Word 文档处理
├── lemon-code-review/           # 代码审查与优化
├── lemon-commit-code/           # 代码提交与推送
├── pdf/                         # PDF 工具包
├── period-report-generator/     # 周期统计报表生成器
├── pptx/                        # PowerPoint 演示文稿处理
├── prompt-engineering/          # 提示词工程
├── publish-blog/                # 博客发布助手
├── skill-creator/               # 技能创建指南
├── slack-gif-creator/           # Slack GIF 创建器
└── web-artifacts-builder/       # Web artifacts 构建器
```

### 目录说明

- **根目录技能**: 自主开发或维护的独立技能
- **agents/**: Claude Code 专用代理，用于特定任务自动化
- **third-party/**: 来自社区的第三方插件集合

## 🎯 技能列表

| 技能名称 | 描述 | 类型 |
|---------|------|------|
| **lemon-commit-code** | 代码提交与推送技能，支持 Conventional Commits 规范，推送到所有仓库 | 开发工具 |
| **lemon-code-review** | 代码审查与优化，支持 Java/Spring/MyBatis 等后端技术栈 | 代码质量 |
| **consumption-statistics** | 自动统计日记中的今日消费清单并填写统计数据 | 生活助手 |
| **period-report-generator** | 根据日记文件生成周/月统计报表，包括血糖、消费、目标完成率 | 数据分析 |
| **publish-blog** | 发布文章从 my-article 知识库到 lemonBlog 静态站点 | 内容管理 |
| **artifacts-builder** | 创建复杂的多组件 claude.ai HTML artifacts（React + Tailwind + shadcn/ui） | 前端开发 |
| **web-artifacts-builder** | 创建基于现代 Web 技术的复杂 artifacts | 前端开发 |
| **canvas-design** | 创建精美的视觉艺术设计（PNG 和 PDF 格式） | 设计工具 |
| **docx** | Word 文档创建、编辑、分析，支持修订、评论、格式保留 | 文档处理 |
| **pdf** | PDF 工具包，支持文本提取、表格处理、表单填写、合并拆分 | 文档处理 |
| **pptx** | 演示文稿创建、编辑、分析，支持布局和演讲者备注 | 文档处理 |
| **changelog-generator** | 从 git commits 自动生成用户友好的 changelog | 文档自动化 |
| **skill-creator** | 创建有效技能的指南，帮助扩展 Claude 能力 | 开发工具 |
| **prompt-engineering** | 优化 LLM 交互的提示工程技能 | 开发工具 |
| **slack-gif-creator** | 创建适合 Slack 的动画 GIF | 媒体工具 |

## 🤖 Agents

本仓库包含 10 个 Claude Code 专用 Agents，来自 [Superpowers 插件](https://github.com/obra/superpowers)，用于自动化处理特定任务。

| Agent | 描述 |
|:---|:---|
| **backend-architect** | 后端系统架构和 API 设计专家 |
| **code-reviewer** | 代码质量、安全性和可维护性审查专家 |
| **context-manager** | 多代理工作流和长时间运行任务的上下文管理专家 |
| **error-detective** | 日志分析和错误模式检测专家 |
| **frontend-developer** | React 应用和响应式设计专家 |
| **fullstack-developer** | 端到端应用开发专家 |
| **performance-engineer** | 性能分析、瓶颈优化和缓存策略专家 |
| **task-decomposition-expert** | 复杂目标分解和工作流编排专家 |
| **technical-researcher** | 代码库分析、技术文档和实现方案研究专家 |
| **test-engineer** | 测试策略、自动化测试和质量保证专家 |

### 使用 Agents

Agents 通常由 Claude Code 自动调用，但也可以通过特定场景触发：

```
# 研究代码库
"帮我研究这个项目的数据库架构"

# 审查代码
"审查我的代码并提供改进建议"

# 性能分析
"分析我的应用性能瓶颈"
```

## 📦 第三方插件

本仓库集成了来自社区的第三方插件集合。

### obsidian-skills

**来源**: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

**作者**: kepano

**描述**: 用于使用 Obsidian 的 Claude Skills，支持创建和编辑 Obsidian 兼容的文件格式。

**包含技能**:

| 技能 | 描述 |
|:---|:---|
| **obsidian-markdown** | 创建和编辑 Obsidian 风格的 Markdown 文件，支持 wikilinks、嵌入、标注、属性等 |
| **obsidian-bases** | 创建和编辑 Obsidian Bases (.base) 文件，支持视图、过滤器、公式和汇总 |
| **json-canvas** | 创建和编辑 JSON Canvas 文件 (.canvas)，支持节点、边、分组和连接 |

**安装方式**:

```powershell
# 复制到 Claude Code 技能目录
Copy-Item -Path "claude-skills\third-party\obsidian-skills\*" -Destination "$env:USERPROFILE\.claude\skills\obsidian-skills\" -Recurse -Force
```

## 🚀 快速开始

### 安装技能

1. **克隆仓库**
   ```bash
   git clone https://github.com/lengmodkx/claude-skills.git
   cd claude-skills
   ```

2. **复制技能到 Claude Code 技能目录**

   **Windows:**
   ```powershell
   Copy-Item -Path "claude-skills\*" -Destination "$env:USERPROFILE\.claude\skills\" -Recurse -Force
   ```

   **macOS/Linux:**
   ```bash
   cp -r claude-skills/* ~/.claude/skills/
   ```

3. **重启 Claude Code** 使技能生效

### 使用技能

在 Claude Code 中，你可以直接使用技能名称：

```
/user: 请帮我审查 /path/to/code.java 中的代码
```

或者通过技能别名触发：

```
/commit
```

## 📚 技能详解

### 🛠️ 开发工具类

#### lemon-commit-code
代码提交与推送技能。自动审查代码、生成符合 Conventional Commits 规范的提交信息，并推送到所有远程仓库（GitHub、Gitee 等）。

**特性：**
- 自动代码审查（安全性、性能、规范）
- 生成规范的提交信息
- 推送到所有远程仓库
- 不添加 AI 署名信息

**使用场景：**
```
提交代码
帮我提交并推送
```

#### lemon-code-review
专业的代码审查与优化技能。针对 Java/Spring/MyBatis 等后端技术栈进行深度审查。

**审查维度：**
- 业务逻辑正确性
- 安全性（SQL注入、XSS、权限校验）
- 性能问题（N+1查询、大对象、循环）
- 代码规范
- 测试覆盖

**使用场景：**
```
审查 UserController.java 的代码
帮我检查这段代码有什么问题
```

#### skill-creator
创建有效技能的指南。帮助你扩展 Claude 的能力，创建定制化的技能。

**包含内容：**
- 技能设计原则
- 工作流程定义
- 最佳实践
- 示例模板

#### prompt-engineering
优化与 LLM 交互的提示工程技能。帮助你编写更有效的提示词。

**应用场景：**
- 编写 Agent 命令
- 创建 Hooks
- 设计子 Agent 提示词
- 优化 LLM 输出

### 📊 数据分析类

#### consumption-statistics
自动统计日记中的今日消费清单并填写统计数据。

**功能：**
- 读取日记文件中的"今日消费清单"表格
- 计算消费笔数、总支出、最大支出、主要类别
- 自动更新到"今日统计"部分

**触发词：** "统计消费"、"填写今日统计"、"消费统计"

#### period-report-generator
根据日记文件生成周期性统计报表（周报/月报）。

**报表内容：**
- 血糖监测分析（空腹、餐后、睡前）
- 消费趋势分析（总支出、日均、主要类别）
- 目标完成情况（计划完成率、工作学习完成率）
- 趋势图表和建议

**触发词：** "生成周报"、"生成月报"、"统计报表"

### 📝 内容管理类

#### publish-blog
从 Obsidian 知识库发布文章到 Next.js 静态博客。

**工作流程：**
1. 复制文章从 my-article/ 到 lemonBlog/content/articles/
2. 添加 format/* 标签
3. 复制关联图片到 img/ 文件夹
4. 运行构建验证
5. 生成符合 Conventional Commits 的提交信息

**触发词：** "发布博客"、"发表文章"、"copy to blog"

#### changelog-generator
从 git commits 自动生成用户友好的发布说明。

**功能：**
- 分析 commit 历史
- 分类变更（Features、Bug Fixes、Breaking Changes）
- 转换技术提交为用户友好的发布说明

### 🎨 设计与媒体类

#### canvas-design
创建精美的视觉艺术设计，导出为 PNG 或 PDF 格式。

**应用场景：**
- 海报设计
- 艺术作品
- 营销材料
- 信息图表

#### slack-gif-creator
创建适合 Slack 分享的动画 GIF。

**约束与验证：**
- 尺寸优化
- 文件大小控制
- 动画效果建议

### 📄 文档处理类

#### docx
Word 文档综合处理工具。

**功能：**
- 创建新文档
- 编辑内容
- 支持修订追踪
- 添加评论
- 保持格式
- 文本提取

#### pdf
PDF 操作工具包。

**功能：**
- 文本和表格提取
- 创建新 PDF
- 合并/拆分文档
- 表单填写
- 批量处理

#### pptx
演示文稿处理工具。

**功能：**
- 创建新演示文稿
- 编辑内容
- 布局管理
- 添加演讲者备注

### 🌐 前端开发类

#### artifacts-builder
创建复杂的多组件 claude.ai HTML artifacts。

**技术栈：**
- React
- Tailwind CSS
- shadcn/ui 组件库

**适用场景：**
- 需要状态管理的 artifacts
- 需要 routing 的应用
- 使用 shadcn/ui 组件

**不适用场景：**
- 简单的单文件 HTML/JSX artifacts

#### web-artifacts-builder
基于现代 Web 技术创建复杂 artifacts。

## 🔧 技能结构

每个技能通常包含以下文件结构：

```
skill-name/
├── skill.md              # 技能主文件（必需）
├── SKILL.md              # 技能描述（某些格式）
├── references/           # 参考文档
│   ├── example.md
│   └── spec.md
├── scripts/              # 脚本文件
│   └── script.py
└── LICENSE.txt           # 许可证
```

### skill.md 文件格式

```yaml
---
name: skill-name
description: 技能描述
license: 许可证信息
---

# 技能标题

技能详细说明...

## 触发场景

描述何时使用此技能

## 工作流程

步骤说明
```

## 🤝 贡献指南

欢迎贡献新的技能或改进现有技能！

### 贡献流程

1. **Fork 本仓库**
2. **创建特性分支** (`git checkout -b feature/AmazingSkill`)
3. **提交更改** (`git commit -m 'feat: Add some AmazingSkill'`)
4. **推送到分支** (`git push origin feature/AmazingSkill`)
5. **创建 Pull Request**

### 技能提交规范

请遵循以下规范：

1. **技能命名**：使用 kebab-case（如 `my-awesome-skill`）
2. **描述清晰**：提供简洁明了的技能描述
3. **文档完整**：包含使用说明和示例
4. **测试验证**：确保技能在 Claude Code 中正常工作

### 技能模板

```yaml
---
name: your-skill-name
description: 简短描述（一句话说明技能用途）
---

# 技能标题

## 触发场景

当用户请求：
- 场景 1
- 场景 2

## 工作流程

### 1. 步骤一

详细说明...

### 2. 步骤二

详细说明...

## 注意事项

1. 注意点 1
2. 注意点 2
```

## 📦 许可证

本项目中的技能可能遵循不同的许可证。请查看每个技能目录中的 `LICENSE.txt` 文件了解详细信息。

除非另有说明，本仓库中的内容遵循 MIT 许可证。

## 🔗 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)
- [Claude API 文档](https://docs.anthropic.com/claude/reference)
- [Claude Agent SDK](https://docs.anthropic.com/claude-agent-sdk)

## 📮 联系方式

- **GitHub**: [@lengmodkx](https://github.com/lengmodkx)
- **Issues**: [提交问题](https://github.com/lengmodkx/claude-skills/issues)

## 🌟 Star History

如果这个项目对你有帮助，请给一个 Star ⭐️

---

<div align="center">

**[⬆ 返回顶部](#claude-code-skills-collection)**

Made with ❤️ by [lengmodkx](https://github.com/lengmodkx)

</div>
