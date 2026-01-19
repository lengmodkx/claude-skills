# 代码审查检查清单

## 1. 业务逻辑检查

### 核心业务规则
- [ ] 业务流程是否符合需求文档
- [ ] 边界条件是否全部覆盖
- [ ] 异常流程是否有合理处理
- [ ] 并发场景是否考虑
- [ ] 数据一致性是否保证

### 数据校验
- [ ] 前端校验后端是否重复校验
- [ ] 必填字段是否校验
- [ ] 数据格式是否校验（邮箱、手机号、日期等）
- [ ] 数值范围是否校验
- [ ] 字符串长度是否限制

## 2. 安全性检查

### SQL 注入
```java
// ❌ 危险 - SQL 注入风险
@Select("SELECT * FROM user WHERE name = '${name}'")

// ✅ 安全 - 使用参数绑定
@Select("SELECT * FROM user WHERE name = #{name}")
```

### XSS 防护
- [ ] 用户输入是否转义
- [ ] 富文本是否特殊处理
- [ ] 页面输出是否编码

### 权限控制
- [ ] 接口是否校验登录状态
- [ ] 是否校验操作权限
- [ ] 敏感数据是否脱敏
- [ ] 越权访问是否防护

### 敏感信息
- [ ] 密码是否加密存储
- [ ] 日志是否记录敏感信息
- [ ] 错误信息是否泄露内部细节

## 3. 性能检查

### 数据库查询
```java
// ❌ N+1 查询问题
List<User> users = userMapper.selectList(wrapper);
for (User user : users) {
    List<Order> orders = orderMapper.selectByUserId(user.getId()); // 循环查询
}

// ✅ 优化 - 批量查询
List<Long> userIds = users.stream().map(User::getId).collect(Collectors.toList());
List<Order> orders = orderMapper.selectByUserIds(userIds);
```

### 索引使用
- [ ] 频繁查询字段是否建索引
- [ ] 联合索引顺序是否合理
- [ ] 避免在索引列上使用函数

### 缓存使用
- [ ] 热点数据是否使用缓存
- [ ] 缓存 key 设计是否合理
- [ ] 缓存过期策略是否合理

### 其他性能
- [ ] 大对象是否延迟加载
- [ ] 循环中是否避免数据库操作
- [ ] 分页是否合理

## 4. 规范检查

### 命名规范
- [ ] 类名使用大驼峰
- [ ] 方法名使用小驼峰
- [ ] 常量全大写下划线分隔
- [ ] 包名全小写

### 代码结构
- [ ] 方法长度是否合理（建议 < 50 行）
- [ ] 类职责是否单一
- [ ] 重复代码是否抽取
- [ ] 注释是否清晰必要

### 异常处理
- [ ] 是否吞掉异常
- [ ] 异常信息是否清晰
- [ ] 是否区分业务异常和技术异常

## 5. Spring 最佳实践

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
- [ ] 事务范围是否合理
- [ ] 是否避免长事务
- [ ] 读写操作是否分开

### 配置管理
- [ ] 硬编码是否避免
- [ ] 配置是否外置
- [ ] 多环境配置是否分离
