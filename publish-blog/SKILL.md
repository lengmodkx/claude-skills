---
name: publish-blog
description: Publish articles from my-article knowledge vault to lemonBlog static site. Use when user wants to publish an Obsidian markdown article to the Next.js blog, including: (1) Copying article from my-article/ to lemonBlog/content/articles/, (2) Adding required format/* tags for publishing, (3) Copying associated images to img/ folders, (4) Running build verification, (5) Generating Conventional Commits compliant git messages. Triggers: "publish blog", "发布博客", "发表文章", "copy to blog", or similar intent to move content from my-article to lemonBlog.
---

# Publish Blog

Publish articles from `my-article/` Obsidian vault to `lemonBlog/content/articles/` for deployment.

## Repository Paths

- **Source**: `D:\lemonArticle\my-article\`
- **Destination**: `D:\lemonArticle\lemonBlog\content\articles\`

## Workflow

### 1. Read Source Article

Use Read tool to read the source markdown file from `my-article/`.

### 2. Validate and Auto-Fix Frontmatter 【CRITICAL】

**必须检查并修复以下格式问题，直到符合发布标准：**

#### 检查清单：

**A. 必需字段检查**
- ✅ `title`: 必须存在且非空
- ✅ `date`: 必须存在，格式为 `YYYY-MM-DD`（不是 `created`！）
- ✅ `category`: 必须是 `技术学习`、`读书笔记`、`日常记录` 之一
- ✅ `tags`: 必须存在且包含 `format/*` 标签

**B. 日期格式验证**
- ❌ 错误：`created: 2025-07-21`
- ✅ 正确：`date: 2024-07-21`
- 日期不能是未来日期（检查是否大于当前日期）
- 如果发现 `created` 字段，必须替换为 `date`

**C. 标签验证**
- 必须包含 `format/article`、`format/reference`、`format/tutorial` 或 `format/note`
- 如果缺少，自动添加 `format/article`

**D. 自动修复示例**

如果 frontmatter 是这样：
```yaml
---
title: "文章标题"
created: 2025-07-21
tags:
  - some-tag
category: 技术学习
---
```

必须自动修复为：
```yaml
---
title: "文章标题"
date: 2024-07-21
tags:
  - some-tag
  - format/article
category: 技术学习
---
```

**修复流程：**
1. 检查是否存在 `created` 字段 → 替换为 `date`
2. 检查日期是否为未来 → 如果是，修改为当前日期或询问用户
3. 检查是否缺少 `category` → 如果缺少，询问用户选择
4. 检查是否缺少 `format/*` 标签 → 如果缺少，自动添加 `format/article`
5. 检查是否缺少 `date` 字段 → 如果缺少，使用当前日期

**修复完成标准：**
所有检查项都通过后，才能进入下一步。

### 3. Select Category 【UPDATED】

如果文章缺少 `category` 字段，使用 AskUserQuestion 工具让用户选择：

```typescript
AskUserQuestion({
  questions: [{
    question: "请选择文章分类",
    header: "分类",
    options: [
      { label: "技术学习", description: "编程、技术文章、教程" },
      { label: "读书笔记", description: "读书总结、书评、阅读笔记" },
      { label: "日常记录", description: "日记、随笔、生活记录" }
    ],
    multiSelect: false
  }]
})
```

用户选择后，使用 Edit 工具在 frontmatter 中添加或更新 `category` 字段。

### 4. Specify Tags Manually 【UPDATED】

使用 AskUserQuestion 工具让用户手动输入标签（逗号分隔，最多5个）：

```typescript
AskUserQuestion({
  questions: [{
    question: "请输入文章标签（用逗号分隔，最多5个）",
    header: "标签",
    multiSelect: false
  }]
})
```

**重要提示：**
- 用户输入的答案会包含逗号分隔的多个标签，例如：`"Java, Spring Boot, 后端开发"`
- 需要将用户输入的字符串按逗号分割成数组
- 限制最多 5 个标签
- 去除每个标签的首尾空格
- **完全替换**文件中的 tags 字段，不保留原有的任何标签
- **自动添加 `format/article` 标签**（如果用户没有指定其他 format/* 标签）

使用 Edit 工具替换 frontmatter 中的 `tags` 字段：

```yaml
---
title: "文章标题"
category: 技术学习
tags:
  - Java
  - Spring Boot
  - 后端开发
  - format/article  # 自动添加
---
```

**标签格式说明：**
- 支持简单标签：`Java`, `MySQL`, `React`
- 支持分类标签：`tech/backend`, `life/photography`
- format/* 标签会自动添加，用户不需要输入

### 5. Generate New Filename

Convert the filename to `YYYY-MM-DD-pinyin-title.md` format:

1. Extract `date` from frontmatter (format: YYYY-MM-DD)
2. Convert `title` to pinyin using pinyin conversion
3. Clean the pinyin: lowercase, replace spaces with hyphens, remove special chars
4. Combine: `{date}-{pinyin-title}.md`

**Example**:
- Title: `kk聊房价` → `kk-liao-fang-jia`
- Date: `2025-09-11`
- Filename: `2025-09-11-kk-liao-fang-jia.md`

**Pinyin Conversion Rules**:
- Use `pinyin` package (already installed in lemonBlog)
- Style: `pinyin.STYLE_NORMAL` (no tones)
- Segment: true (for better word separation)
- Remove special characters, keep only a-z, 0-9, and hyphens
- Convert to lowercase

**Node.js code example for pinyin conversion**:
```javascript
import pinyin from 'pinyin';

function generateFilename(title, date) {
  const pinyinResult = pinyin(title, {
    style: pinyin.STYLE_NORMAL,
    heteronym: false,
    segment: true
  }).flat().join('-');

  const clean = pinyinResult
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');

  return `${date}-${clean}.md`;
}
```

### 6. Copy Article to Destination

Use the generated filename from step 5, copy to:
`lemonBlog/content/articles/{YYYY-MM-DD-pinyin-title}.md`

### 7. Upload Images to Aliyun OSS 【UPDATED】

将文章中的图片上传到阿里云OSS并自动替换链接。

使用 Bash 工具运行上传脚本：

```bash
cd D:\lemonArticle\lemonBlog
node scripts/upload-to-oss.js "content/articles/{slug}.md" "blog/images/"
```

**脚本功能：**
1. 扫描文章目录 `content/articles/{slug}/img/` 中的所有图片
2. 批量上传到 OSS Bucket 的 `blog/images/{slug}/` 路径
3. 将 markdown 中的本地图片链接替换为 OSS URL
4. 生成上传报告

**环境变量要求：**
确保 `.env.local` 文件已配置 OSS 信息：
```bash
OSS_REGION=oss-cn-hangzhou
OSS_ACCESS_KEY_ID=your_key
OSS_ACCESS_KEY_SECRET=your_secret
OSS_BUCKET=your-bucket
OSS_PREFIX=blog/images/
```

**示例：**
- 本地路径: `img/1-1.jpg`
- OSS路径: `blog/images/2025-07-21-sony-a6700-guide/1-1.jpg`
- OSS URL: `https://your-bucket.oss-cn-hangzhou.aliyuncs.com/blog/images/2025-07-21-sony-a6700-guide/1-1.jpg`

**注意：**
- 上传后的图片链接会自动写入文章
- 不再需要复制图片到 `public/` 目录
- 如果没有图片或OSS未配置，跳过此步骤

### 8. Verify Build

Navigate to lemonBlog directory and run:

```bash
cd D:\lemonArticle\lemonBlog
npm run build
```

If build fails, fix errors before proceeding.

### 9. Git Commit

Change to lemonBlog directory and check git status:

```bash
cd D:\lemonArticle\lemonBlog
git status
git diff
```

Generate Conventional Commits compliant message:

```
docs(blog): publish {article-title}

- Add article: {title}
- Copy images from my-article
- Build verified
```

Use `git add` and `git commit` with generated message.

## Frontmatter Reference

### Required for Publishing

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Article title (Chinese or English) |
| `created` | string | Date in YYYY-MM-DD format (used for slug generation) |
| `tags` | array | Must include `format/*` tag |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `updated` | string | Last update date (YYYY-MM-DD) |
| `type` | string | Content type (e.g., "技术文档", "笔记") |
| `status` | string | Content status (e.g., "done", "draft") |
| `author` | string | Author name (supports `[[wikilink]]` syntax) |
| `description` | string | Brief description for SEO |
| `source` | string | Source URL if content is from another site |

## Git Commit Message Format

Use Conventional Commits specification:

```
{type}({scope}): {subject}

{body}
```

**Types**:
- `docs(blog)` - Publishing new blog article
- `fix(blog)` - Fixing published article
- `chore(blog)` - Blog maintenance tasks

**Example**:
```
docs(blog): publish MySQL中文拼音排序问题

- Add article from my-article/博客文章/
- Copy images to public/articles/2025-09-10-mysql-zhong-wen-pin-yin-pai-xu-wen-ti/img/
- Frontmatter updated with format/reference tag
- Build verification passed
```

## Common Issues

### Article not appearing on site

Check that `format/*` tag exists in frontmatter. Articles without this tag are filtered out during build.

### Images not loading

Ensure images are copied to `public/articles/{slug}/img/` and referenced correctly in markdown:
- Per-article: `![alt](img/filename.jpg)`
- Shared: `![alt](img/filename.jpg)`

### Build fails

Check for:
- Invalid YAML in frontmatter
- Missing required fields
- Image path errors
- TypeScript errors in components
