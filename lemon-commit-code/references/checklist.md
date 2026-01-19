# 代码审查检查清单

## 1. 业务逻辑检查

### 核心功能
- [ ] 业务流程是否符合需求
- [ ] 边界条件是否全部覆盖
- [ ] 异常流程是否处理
- [ ] 并发场景是否考虑
- [ ] 数据一致性是否保证

### 数据校验
- [ ] 必填字段校验
- [ ] 数据格式校验（邮箱、手机号、日期）
- [ ] 数值范围校验
- [ ] 字符串长度限制

## 2. 安全性检查

### SQL 注入
```java
// ❌ 危险
@Select("SELECT * FROM user WHERE name = '${name}'")

// ✅ 安全
@Select("SELECT * FROM user WHERE name = #{name}")
```

### XSS 防护
- [ ] 用户输入是否转义
- [ ] 富文本是否特殊处理
- [ ] 页面输出是否编码

### 权限控制
- [ ] 接口校验登录状态
- [ ] 校验操作权限
- [ ] 敏感数据脱敏
- [ ] 越权访问防护

### 敏感信息
- [ ] 密码加密存储
- [ ] 日志不记录敏感信息
- [ ] 错误信息不泄露内部细节

## 3. 性能检查

### 数据库
```java
// ❌ N+1 查询
for (User user : users) {
    List<Order> orders = orderMapper.selectByUserId(user.getId());
}

// ✅ 批量查询
List<Long> ids = users.stream().map(User::getId).collect(Collectors.toList());
List<Order> orders = orderMapper.selectByUserIds(ids);
```

### 索引
- [ ] 频繁查询字段建索引
- [ ] 联合索引顺序合理
- [ ] 避免索引列使用函数

### 缓存
- [ ] 热点数据使用缓存
- [ ] 缓存key设计合理
- [ ] 缓存过期策略合理

## 4. 规范检查

### 命名规范
- [ ] 类名大驼峰
- [ ] 方法名小驼峰
- [ ] 常量全大写下划线
- [ ] 包名全小写

### 代码结构
- [ ] 方法长度合理（建议 < 50行）
- [ ] 类职责单一
- [ ] 重复代码抽取
- [ ] 注释清晰必要

### 异常处理
- [ ] 不吞掉异常
- [ ] 异常信息清晰
- [ ] 区分业务异常和技术异常

## 5. Java/Spring 规范

### 依赖注入
```java
// ❌ 字段注入（不推荐）
@Autowired
private UserService userService;

// ✅ 构造器注入（推荐）
private final UserService userService;
public UserController(UserService userService) {
    this.userService = userService;
}
```

### 事务管理
- [ ] 事务范围合理
- [ ] 避免长事务
- [ ] 读写操作分开

### 配置
- [ ] 无硬编码
- [ ] 配置外置
- [ ] 多环境配置分离

## 6. Git 提交规范

### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug修复 |
| refactor | 重构 |
| docs | 文档 |
| style | 格式 |
| test | 测试 |
| chore | 构建 |

### 提交信息要求
- [ ] Subject 简洁明了（50字符内）
- [ ] Body 详细说明变更原因和方式
- [ ] Footer 注明重大变更和关单信息

## 7. 禁止提交

- ❌ 敏感信息（密钥、密码、Token）
- ❌ 编译产物（target/、*.class）
- ❌ IDE 配置（.idea、*.iml）
- ❌ 本地配置文件（application-local.yml）
- ❌ 无意义提交（"fix"、"update"）
- ❌ AI 工具署名信息（Co-Authored-By、Generated with）
