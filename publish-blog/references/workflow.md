# Publishing Workflow

Step-by-step process for publishing articles from my-article to lemonBlog.

## Pre-Publishing Checklist

Before starting, verify:
- [ ] Article exists in `my-article/` directory
- [ ] Article has required frontmatter fields
- [ ] Images (if any) are in appropriate folders
- [ ] Article is ready for publication

## Step-by-Step Process

### Step 1: Read Source Article

Identify the source article path and read its content:

```
Source: D:\lemonArticle\my-article\博客文章\article-name.md
       D:\lemonArticle\my-article\开发技能\topic\article-name.md
```

Use Read tool to get the full content.

### Step 2: Validate and Update Frontmatter

Check for required fields:

```yaml
title: "required"      # Must exist
created: YYYY-MM-DD    # Must exist
tags:                  # Must include format/*
  - format/xxx
```

**If `format/*` tag is missing**, add it:

1. Identify appropriate format tag:
   - `format/article` - Original blog post
   - `format/reference` - Reference/translation
   - `format/tutorial` - Tutorial content
   - `format/note` - Quick note

2. Add to tags array using Edit tool

### Step 3: Determine Destination Path

Destination format: `D:\lemonArticle\lemonBlog\content\articles\{filename}.md`

Use the original filename or create a descriptive name based on the article title.

### Step 4: Copy Article Content

Use Write tool to create the article at destination path with the same content.

### Step 5: Handle Images

#### Identify Image Locations

Check article content for image references:
- Markdown syntax: `![alt](path/to/image.jpg)`
- HTML syntax: `<img src="path/to/image.jpg">`

#### Per-Article Images

If article has `img/` folder next to it:

```
Source: D:\lemonArticle\my-article\博客文章\article-name\img\
Dest:   D:\lemonArticle\lemonBlog\public\articles\{slug}\img\
```

Use Bash commands:

```bash
# Create destination directory
mkdir -p "D:\lemonArticle\lemonBlog\public\articles\{slug}\img"

# Copy images
copy "D:\lemonArticle\my-article\source\img\*" "D:\lemonArticle\lemonBlog\public\articles\{slug}\img\"
```

#### Shared Images

If using shared `img/` folder:

```
Source: D:\lemonArticle\my-article\img\
Dest:   D:\lemonArticle\lemonBlog\public\articles\img\
```

#### External Images

No action needed for external URLs (https://...).

### Step 6: Verify Build

Navigate to lemonBlog and run build:

```bash
cd D:\lemonArticle\lemonBlog
npm run build
```

**If build succeeds**: Proceed to commit
**If build fails**: Fix errors before proceeding

Common build issues:
- Invalid YAML in frontmatter
- Missing required fields
- Image path errors
- TypeScript errors

### Step 7: Git Operations

#### Check Status

```bash
cd D:\lemonArticle\lemonBlog
git status
git diff
```

#### Stage Files

```bash
git add content/articles/{filename}.md
git add public/articles/{slug}/img/
```

#### Generate Commit Message

Use Conventional Commits format:

```
docs(blog): publish {article-title}

- Add article: {title}
- Copy images from {source-path}
- Frontmatter updated with {format-tag} tag
- Build verification passed
```

#### Commit

```bash
git commit -m "generated commit message"
```

#### Optional: Push

```bash
git push
```

## Example Complete Workflow

```
User: Publish "MySQL 中文拼音排序问题" to blog

1. Read source:
   D:\lemonArticle\my-article\博客文章\MySQL 索引类型与索引方法详解.md

2. Validate frontmatter:
   ✅ title: "MySQL 中文拼音排序问题"
   ✅ created: 2025-09-10
   ✅ tags: includes format/reference

3. Copy to:
   D:\lemonArticle\lemonBlog\content\articles\mysql-sorting.md

4. Copy images:
   From: my-article\博客文章\mysql-sorting\img\
   To:   lemonBlog\public\articles\mysql-sorting\img\

5. Verify build:
   cd lemonBlog && npm run build
   ✅ Build successful

6. Git commit:
   cd lemonBlog
   git add content/articles/mysql-sorting.md
   git add public/articles/mysql-sorting/img/
   git commit -m "docs(blog): publish MySQL中文拼音排序问题

- Add article from my-article/博客文章/
- Copy images to public/articles/mysql-sorting/img/
- Frontmatter updated with format/reference tag
- Build verification passed"
```

## Troubleshooting

### Article not appearing on site

**Cause**: Missing `format/*` tag
**Fix**: Add appropriate format tag to frontmatter

### Images showing as broken

**Cause**: Images not in `public/articles/` or wrong path
**Fix**: Copy images to correct location and verify markdown references

### Build fails with frontmatter error

**Cause**: Invalid YAML syntax
**Fix**: Check YAML indentation, quote strings with colons, use proper array syntax

### Slug generation issues

**Cause**: Missing or invalid `created` date
**Fix**: Ensure `created` field exists in YYYY-MM-DD format
