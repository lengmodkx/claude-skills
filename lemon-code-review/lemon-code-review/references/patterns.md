# 常见问题与优化模式

## 1. 空指针问题

### 场景一：对象属性访问
```java
// ❌ 风险代码
public User getUser(Long id) {
    User user = userMapper.selectById(id);
    return user.getName(); // 如果 user 为 null，抛出 NPE
}

// ✅ 安全写法
public String getUserName(Long id) {
    User user = userMapper.selectById(id);
    return user != null ? user.getName() : null;
}

// 或使用 Optional
public String getUserName(Long id) {
    return Optional.ofNullable(userMapper.selectById(id))
            .map(User::getName)
            .orElse(null);
}
```

### 场景二：集合操作
```java
// ❌ 风险代码
List<User> users = userMapper.selectList(wrapper);
return users.get(0).getName(); // 空列表会抛 IndexOutOfBoundsException

// ✅ 安全写法
List<User> users = userMapper.selectList(wrapper);
return users.isEmpty() ? null : users.get(0).getName();
```

## 2. SQL 注入与参数绑定

### MyBatis 参数处理
```java
// ❌ 危险 - 使用 ${} 直接拼接
@Select("SELECT * FROM user WHERE name = '${name}'")
List<User> selectByName(String name);

// ✅ 安全 - 使用 #{} 参数绑定
@Select("SELECT * FROM user WHERE name = #{name}")
List<User> selectByName(@Param("name") String name);
```

### 动态 SQL 安全
```xml
<!-- ❌ 危险 - 动态拼接可能导致注入 -->
<select id="findByCondition" resultType="User">
    SELECT * FROM user
    WHERE 1=1
    <if test="condition != null">
        AND ${condition}
    </if>
</select>

<!-- ✅ 安全 - 使用参数化查询 -->
<select id="findByCondition" resultType="User">
    SELECT * FROM user
    <where>
        <if test="name != null">
            AND name = #{name}
        </if>
        <if test="status != null">
            AND status = #{status}
        </if>
    </where>
</select>
```

## 3. 循环查询问题（N+1）

```java
// ❌ N+1 问题
public List<UserDTO> getUserWithOrders() {
    List<User> users = userMapper.selectList(null);
    List<UserDTO> result = new ArrayList<>();
    for (User user : users) {
        // 循环内每次查询
        List<Order> orders = orderMapper.selectByUserId(user.getId());
        result.add(convert(user, orders));
    }
    return result;
}

// ✅ 优化方案 - 批量查询
public List<UserDTO> getUserWithOrders() {
    List<User> users = userMapper.selectList(null);
    if (users.isEmpty()) {
        return Collections.emptyList();
    }
    Set<Long> userIds = users.stream()
            .map(User::getId)
            .collect(Collectors.toSet());
    Map<Long, List<Order>> orderMap = orderMapper.selectByUserIds(userIds)
            .stream()
            .collect(Collectors.groupingBy(Order::getUserId));

    return users.stream()
            .map(user -> convert(user, orderMap.getOrDefault(user.getId(), Collections.emptyList())))
            .collect(Collectors.toList());
}
```

## 4. 并发安全问题

### 线程安全
```java
// ❌ 非线程安全
public class Counter {
    private int count = 0;
    public void increment() {
        count++;
    }
}

// ✅ 线程安全 - 使用 AtomicInteger
public class Counter {
    private final AtomicInteger count = new AtomicInteger(0);
    public void increment() {
        count.incrementAndGet();
    }
}

// ✅ 线程安全 - 使用 synchronized
public class Counter {
    private int count = 0;
    public synchronized void increment() {
        count++;
    }
}
```

### 共享状态
```java
// ❌ 共享可变状态
public class SharedService {
    private static String sharedState; // 危险：静态字段

    public void setState(String value) {
        sharedState = value;
    }
}

// ✅ 使用参数传递或 ThreadLocal
public class SafeService {
    public void process(String state) {
        // 使用局部变量，不共享状态
    }
}
```

## 5. 异常处理模式

### 业务异常
```java
// 定义业务异常
public class BusinessException extends RuntimeException {
    private final Integer errorCode;

    public BusinessException(Integer errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }
}

// 使用
if (user == null) {
    throw new BusinessException(404, "用户不存在");
}
```

### 全局异常处理
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<?> handleBusinessException(BusinessException e) {
        return Result.error(e.getErrorCode(), e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public Result<?> handleException(Exception e) {
        log.error("系统异常", e);
        return Result.error(500, "系统繁忙，请稍后重试");
    }
}
```

## 6. 资源关闭

```java
// ❌ 资源未关闭
public void readFile() {
    BufferedReader reader = new BufferedReader(new FileReader("file.txt"));
    String line = reader.readLine();
    // reader 未关闭
}

// ✅ 使用 try-with-resources
public void readFile() {
    try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
        String line = reader.readLine();
        // 处理逻辑
    } catch (IOException e) {
        log.error("读取文件失败", e);
    }
}

// ✅ 或使用 Spring 的 ResourceUtils
public void readFile() {
    try (InputStream is = new ClassPathResource("file.txt").getInputStream()) {
        // 处理逻辑
    } catch (IOException e) {
        log.error("读取文件失败", e);
    }
}
```

## 7. 事务使用

### 事务传播
```java
// ❌ 事务范围过大
@Transactional
public void process() {
    validate();      // 校验不需要事务
    saveData();      // 需要事务
    sendNotification(); // 远程调用，可能超时
}

// ✅ 拆分事务
@Transactional(readOnly = true)
public void validate() {
    // 校验逻辑
}

@Transactional
public void saveData() {
    // 保存逻辑
}

public void sendNotification() {
    // 通知逻辑，不使用事务
}
```

### 事务隔离
```java
// 读已提交数据，避免脏读
@Transactional(isolation = Isolation.READ_COMMITTED)
public User getUser(Long id) {
    return userMapper.selectById(id);
}
```

## 8. 缓存使用

```java
// ❌ 缓存穿透
public User getUser(Long id) {
    User user = cache.get(id);
    if (user == null) {
        user = userMapper.selectById(id);
        if (user != null) {
            cache.put(id, user);
        }
    }
    return user;
}

// ✅ 缓存空值防止穿透
public User getUser(Long id) {
    User user = cache.get(id);
    if (user != null) {
        return user;
    }
    user = userMapper.selectById(id);
    // 缓存空对象，设置较短的过期时间
    cache.put(id, user != null ? user : EMPTY_USER, 5, TimeUnit.MINUTES);
    return user;
}

// ✅ 使用 Spring Cache
@Cacheable(value = "users", key = "#id")
public User getUser(Long id) {
    return userMapper.selectById(id);
}

@CacheEvict(value = "users", key = "#user.id")
public void updateUser(User user) {
    userMapper.updateById(user);
}
```
