# Git Commit Message Specification

Conventional Commits format for lemonBlog.

## Format

```
{type}({scope}): {subject}

{body}

{footer}
```

## Types

| Type | Usage | Example |
|------|-------|---------|
| `docs` | Publishing new articles or documentation | `docs(blog): publish MySQL排序问题` |
| `fix` | Bug fixes in published articles | `fix(blog): correct typo in article` |
| `chore` | Maintenance tasks | `chore(blog): update dependencies` |
| `feat` | New features | `feat(blog): add comment system` |
| `refactor` | Code refactoring | `refactor(blog): optimize build process` |

## Scopes

| Scope | Usage |
|-------|-------|
| `blog` | Blog content and configuration |
| `content` | Article content only |
| `image` | Image assets |
| `build` | Build configuration |

## Subject

- Use present tense ("add" not "added")
- Use imperative mood ("move" not "moves")
- Limit to 50 characters
- Do NOT end with period
- Reference the article title if applicable

## Body

- Explain what and why (not how)
- Wrap at 72 characters
- Use bullet points for multiple changes

## Examples

### Publishing a new article

```
docs(blog): publish MySQL中文拼音排序问题

- Add article from my-article/博客文章/
- Copy images to public/articles/2025-09-10-mysql-zhong-wen-pin-yin-pai-xu-wen-ti/img/
- Frontmatter updated with format/reference tag
- Build verification passed
```

### Fixing an article

```
fix(blog): correct code example in MySQL排序问题

- Fixed SQL syntax error in CREATE TABLE example
- Updated screenshot for clarity
```

### Updating images only

```
chore(image): update preview images for MySQL article

- Replace blurry screenshot with high-quality version
- Optimize image sizes for faster loading
```

### Multiple articles

```
docs(blog): publish 3 new articles

- Add MySQL中文拼音排序问题
- Add Java线程池 tutorial
- Add Redis缓存设计 patterns
- All articles verified with npm run build
```

## Commit Workflow

1. Check git status to see changes
2. Review diff to ensure correctness
3. Generate commit message following format
4. Use git add to stage files
5. Commit with generated message
6. Optionally push to remote

```bash
cd D:\lemonArticle\lemonBlog
git status
git diff
git add .
git commit -m "docs(blog): publish article title"
git push
```
