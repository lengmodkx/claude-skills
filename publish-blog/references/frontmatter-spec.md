# LemonBlog Frontmatter Specification

Complete frontmatter schema for lemonBlog articles.

## Required Fields for Publishing

### title
- **Type**: String
- **Required**: Yes
- **Description**: Article title in Chinese or English
- **Example**: `title: "MySQL 中文拼音排序问题"`

### created
- **Type**: String (YYYY-MM-DD format)
- **Required**: Yes
- **Description**: Publication date, used for slug generation
- **Example**: `created: 2025-09-10`

### tags
- **Type**: Array of strings
- **Required**: Yes, must include `format/*`
- **Description**: Article categorization and publishing control
- **Important**: Articles without `format/*` tag are NOT published

## Format Tags (Required for Publishing)

The blog filters articles by `format/*` tags. Without one, the article is excluded during build.

| Tag | Usage |
|-----|-------|
| `format/article` | Regular blog post |
| `format/reference` | Reference material or documentation |
| `format/tutorial` | Tutorial or how-to content |
| `format/note` | Technical note or quick reference |

## Category Tags (Optional)

Common category tags used in the blog:

| Tag | Category |
|-----|----------|
| `tech/mysql` | MySQL database |
| `tech/backend` | Backend development |
| `tech/frontend` | Frontend development |
| `tech/java` | Java programming |
| `tech/algorithm` | Algorithms |
| `tech/database` | Databases |
| `devops/*` | DevOps topics |

## Optional Fields

### updated
- **Type**: String (YYYY-MM-DD format)
- **Description**: Last update date
- **Example**: `updated: '2025-09-11'`

### type
- **Type**: String
- **Description**: Content type classification
- **Examples**: `技术文档`, `笔记`, `教程`

### status
- **Type**: String
- **Description**: Content status
- **Examples**: `done`, `draft`, `doing`

### author
- **Type**: String or Array
- **Description**: Author name(s)
- **Supports**: Obsidian `[[wikilink]]` syntax
- **Examples**:
  ```yaml
  author: '[[沃夫上校]]'
  # or
  author:
    - '[[Author One]]'
    - '[[Author Two]]'
  ```

### description
- **Type**: String
- **Description**: Brief description for SEO and previews
- **Example**: `description: "A comprehensive guide to MySQL Chinese pinyin sorting"`

### source
- **Type**: String (URL)
- **Description**: Source URL if content is from another site
- **Example**: `source: https://juejin.cn/post/7547989975469719562`

## Complete Example

```yaml
---
title: MySQL 中文拼音排序问题
type: 技术文档
status: done
tags:
  - tech/mysql
  - format/reference
  - tech/backend
created: 2025-09-10
updated: '2025-09-11'
author:
  - '[[沃夫上校]]'
source: https://juejin.cn/post/7547989975469719562
---
```

## Minimal Example (for publishing)

```yaml
---
title: "文章标题"
created: 2025-09-10
tags:
  - format/article
---
```

## Slug Generation

Slugs are auto-generated from `created` date + `title` (converted to pinyin):

- Input: `title: "MySQL 中文拼音排序问题"`, `created: "2025-09-10"`
- Output: `2025-09-10-mysql-zhong-wen-pin-yin-pai-xu-wen-ti`

Slug generation is handled by `src/lib/slugify.ts` using the `pinyin` npm package.
