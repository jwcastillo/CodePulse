# Spring Framework Analysis Guide - CodePulse 2.0

## Overview

This guide demonstrates how to use CodePulse to analyze Spring Framework applications for anti-patterns, security vulnerabilities, and optimization opportunities across:

- **Spring Data JPA** - Database access and ORM patterns
- **Spring Security** - Authentication, authorization, and security
- **Spring REST API** - RESTful API design and best practices

## Quick Start

### Spring Data JPA Analysis

```python
from pathlib import Path
from analyzers.java.spring_data_analyzer import SpringDataAnalyzer
from reporters import ConsoleReporter

# Create analyzer
analyzer = SpringDataAnalyzer()

# Analyze your Spring Data JPA code
result = analyzer.analyze_directory(Path("./src"))

# View results
ConsoleReporter(use_colors=True, verbose=True).report(result)
```

### Spring Security Analysis

```python
from pathlib import Path
from analyzers.java.spring_security_analyzer import SpringSecurityAnalyzer
from reporters import HTMLReporter

# Create analyzer
analyzer = SpringSecurityAnalyzer()

# Analyze your Spring Security configuration
result = analyzer.analyze_directory(Path("./src"))

# Generate HTML report
HTMLReporter().report(result, Path("./security-report.html"))
```

### Spring REST API Analysis

```python
from pathlib import Path
from analyzers.java.spring_rest_analyzer import SpringRestAnalyzer
from reporters import JSONReporter

# Create analyzer
analyzer = SpringRestAnalyzer()

# Analyze your REST controllers
result = analyzer.analyze_directory(Path("./src"))

# Generate JSON report for CI/CD
JSONReporter().report(result, Path("./api-report.json"))
```

---

## Spring Data JPA Anti-Patterns

### 1. N+1 Query Problem (CRITICAL)

**Issue**: Lazy loading entities in a loop

**Before:**
```java
@Service
public class UserService {
    public void processUsers(List<User> users) {
        for (User user : users) {
            List<Order> orders = user.getOrders(); // N+1 queries!
            processOrders(orders);
        }
    }
}
```

**After:**
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    @EntityGraph(attributePaths = "orders")
    List<User> findAllWithOrders();
}

@Service
public class UserService {
    public void processUsers() {
        List<User> users = userRepository.findAllWithOrders(); // 1 query
        for (User user : users) {
            processOrders(user.getOrders());
        }
    }
}
```

**Impact**: 1000 users = 1001 queries → 1 query (100x faster)

---

### 2. Repository Call in Loop (CRITICAL)

**Issue**: Database queries inside loops

**Before:**
```java
public void loadOrders(List<Long> orderIds) {
    for (Long id : orderIds) {
        Order order = orderRepository.findById(id).orElse(null);
        process(order);
    }
}
```

**After:**
```java
public void loadOrders(List<Long> orderIds) {
    List<Order> orders = orderRepository.findAllById(orderIds);
    orders.forEach(this::process);
}
```

**Impact**: N iterations = N queries → 1 query

---

### 3. Missing Pagination (HIGH)

**Issue**: Loading entire tables into memory

**Before:**
```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findAll(); // Loads all products!
}
```

**After:**
```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    Page<Product> findAll(Pageable pageable);
}

// Usage
Page<Product> products = repository.findAll(
    PageRequest.of(0, 20, Sort.by("name"))
);
```

**Impact**: Prevents OutOfMemoryError with large datasets

---

### 4. Save in Loop (HIGH)

**Issue**: Individual saves instead of batch

**Before:**
```java
public void saveProducts(List<Product> products) {
    for (Product product : products) {
        productRepository.save(product); // N database trips
    }
}
```

**After:**
```java
public void saveProducts(List<Product> products) {
    productRepository.saveAll(products); // Batch operation
}

// Configure batch size in application.properties
spring.jpa.properties.hibernate.jdbc.batch_size=20
```

**Impact**: N saves → 1 batch (10-50x faster)

---

### 5. Missing @Transactional (MEDIUM)

**Issue**: Data modifications without transaction management

**Before:**
```java
@Service
public class OrderService {
    public void createOrder(OrderRequest request) {
        Order order = new Order();
        orderRepository.save(order); // No transaction!
    }
}
```

**After:**
```java
@Service
public class OrderService {
    @Transactional
    public void createOrder(OrderRequest request) {
        Order order = new Order();
        orderRepository.save(order);
    }
}
```

**Impact**: Ensures data consistency and automatic rollback on errors

---

## Spring Security Vulnerabilities

### 1. CSRF Protection Disabled (CRITICAL)

**Issue**: Application vulnerable to CSRF attacks

**Before:**
```java
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable(); // DANGEROUS!
        return http.build();
    }
}
```

**After:**
```java
@Configuration
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf()
            .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse());
        return http.build();
    }
}
```

**Impact**: Prevents Cross-Site Request Forgery attacks

---

### 2. CORS Allow All Origins (CRITICAL)

**Issue**: Any website can make requests to your API

**Before:**
```java
@Configuration
public class CorsConfig {
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                    .allowedOrigins("*"); // Security risk!
            }
        };
    }
}
```

**After:**
```java
@Configuration
public class CorsConfig {
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins("https://trusted-domain.com")
                    .allowedMethods("GET", "POST", "PUT", "DELETE")
                    .allowCredentials(true);
            }
        };
    }
}
```

**Impact**: Prevents unauthorized cross-origin requests

---

### 3. Hardcoded Credentials (CRITICAL)

**Issue**: Credentials exposed in source code

**Before:**
```java
@Configuration
public class DatabaseConfig {
    private String apiKey = "sk_live_1234567890abcdef"; // EXPOSED!
}
```

**After:**
```java
@Configuration
public class DatabaseConfig {
    @Value("${api.key}")
    private String apiKey;
}

# application.properties or environment variable
API_KEY=${API_KEY}
```

**Impact**: Prevents credential exposure in version control

---

### 4. Weak Password Encoder (CRITICAL)

**Issue**: Passwords easily cracked

**Before:**
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return NoOpPasswordEncoder.getInstance(); // Plain text!
}
```

**After:**
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // Strong hashing
}
```

**Impact**: Protects passwords with strong hashing algorithm

---

### 5. Permit All Endpoints (CRITICAL)

**Issue**: No authentication required

**Before:**
```java
http.authorizeRequests()
    .anyRequest().permitAll(); // Everything public!
```

**After:**
```java
http.authorizeRequests()
    .antMatchers("/public/**", "/health").permitAll()
    .anyRequest().authenticated();
```

**Impact**: Enforces authentication for protected resources

---

## Spring REST API Anti-Patterns

### 1. Missing @Valid Annotation (HIGH)

**Issue**: Unvalidated input

**Before:**
```java
@PostMapping("/users")
public ResponseEntity<User> createUser(@RequestBody UserRequest request) {
    return ResponseEntity.ok(userService.create(request));
}
```

**After:**
```java
@PostMapping("/users")
public ResponseEntity<User> createUser(
    @Valid @RequestBody UserRequest request) {
    return ResponseEntity.ok(userService.create(request));
}

// UserRequest DTO
public class UserRequest {
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 50)
    private String name;

    @Email(message = "Invalid email")
    @NotBlank
    private String email;
}
```

**Impact**: Prevents invalid data and security vulnerabilities

---

### 2. Entity in Request/Response (HIGH)

**Issue**: JPA entities exposed directly

**Before:**
```java
@PostMapping("/users")
public User createUser(@RequestBody UserEntity entity) {
    return userRepository.save(entity); // Mass assignment risk!
}
```

**After:**
```java
@PostMapping("/users")
public UserResponse createUser(@Valid @RequestBody UserRequest request) {
    UserEntity entity = userMapper.toEntity(request);
    UserEntity saved = userRepository.save(entity);
    return userMapper.toResponse(saved);
}
```

**Impact**: Prevents mass assignment, tight coupling, and data exposure

---

### 3. List Without Pagination (HIGH)

**Issue**: Performance problems with large datasets

**Before:**
```java
@GetMapping("/users")
public List<User> getUsers() {
    return userRepository.findAll(); // All users!
}
```

**After:**
```java
@GetMapping("/users")
public Page<UserResponse> getUsers(
    @PageableDefault(size = 20) Pageable pageable) {
    Page<User> users = userRepository.findAll(pageable);
    return users.map(userMapper::toResponse);
}
```

**Impact**: Handles large datasets efficiently

---

### 4. GET Request with Request Body (HIGH)

**Issue**: Violates HTTP semantics

**Before:**
```java
@GetMapping("/search")
public List<User> search(@RequestBody SearchRequest request) {
    return userService.search(request);
}
```

**After:**
```java
@PostMapping("/search")
public List<User> search(@Valid @RequestBody SearchRequest request) {
    return userService.search(request);
}
```

**Impact**: Follows HTTP standards, better caching

---

### 5. Stack Trace in Response (CRITICAL)

**Issue**: Information disclosure vulnerability

**Before:**
```java
@GetMapping("/users/{id}")
public ResponseEntity<User> getUser(@PathVariable Long id) {
    try {
        return ResponseEntity.ok(userService.find(id));
    } catch (Exception e) {
        e.printStackTrace(); // Logs to console
        return ResponseEntity.badRequest().body(null);
    }
}
```

**After:**
```java
@GetMapping("/users/{id}")
public ResponseEntity<UserResponse> getUser(@PathVariable Long id) {
    User user = userService.find(id);
    return ResponseEntity.ok(userMapper.toResponse(user));
}

@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(
        UserNotFoundException ex) {
        logger.error("User not found: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("User not found"));
    }
}
```

**Impact**: Prevents information disclosure, better error handling

---

## Combined Analysis

Run all Spring analyzers together:

```python
from pathlib import Path
from analyzers.java.spring_data_analyzer import SpringDataAnalyzer
from analyzers.java.spring_security_analyzer import SpringSecurityAnalyzer
from analyzers.java.spring_rest_analyzer import SpringRestAnalyzer
from reporters import ConsoleReporter, HTMLReporter
from core import AnalysisResult

# Create analyzers
data_analyzer = SpringDataAnalyzer()
security_analyzer = SpringSecurityAnalyzer()
rest_analyzer = SpringRestAnalyzer()

# Analyze
data_result = data_analyzer.analyze_directory(Path("./src"))
security_result = security_analyzer.analyze_directory(Path("./src"))
rest_result = rest_analyzer.analyze_directory(Path("./src"))

# Combine results
all_issues = data_result.issues + security_result.issues + rest_result.issues
combined = AnalysisResult(issues=all_issues)

# Console report
ConsoleReporter().report(combined)

# HTML report
HTMLReporter().report(combined, Path("./spring-analysis.html"))
```

---

## Filter by Severity and Category

```python
from core import Severity, Category

# Get critical security issues
critical_security = [
    issue for issue in combined.issues
    if issue.severity == Severity.CRITICAL and
       issue.category == Category.SECURITY
]

# Get all performance issues
performance = [
    issue for issue in combined.issues
    if issue.category == Category.PERFORMANCE
]

# Get API design issues
api_design = [
    issue for issue in combined.issues
    if issue.category == Category.API_DESIGN
]

print(f"🔴 Critical Security Issues: {len(critical_security)}")
print(f"⚡ Performance Issues: {len(performance)}")
print(f"🔌 API Design Issues: {len(api_design)}")
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Spring Code Quality Check

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install CodePulse
        run: pip install codepulse

      - name: Run Spring Analysis
        run: |
          python3 << 'EOF'
          from pathlib import Path
          from analyzers.java.spring_data_analyzer import SpringDataAnalyzer
          from analyzers.java.spring_security_analyzer import SpringSecurityAnalyzer
          from analyzers.java.spring_rest_analyzer import SpringRestAnalyzer
          from reporters import JSONReporter
          from core import Severity, AnalysisResult
          import sys

          # Run all analyzers
          data = SpringDataAnalyzer().analyze_directory(Path("./src"))
          security = SpringSecurityAnalyzer().analyze_directory(Path("./src"))
          rest = SpringRestAnalyzer().analyze_directory(Path("./src"))

          # Combine results
          all_issues = data.issues + security.issues + rest.issues
          combined = AnalysisResult(issues=all_issues)

          # Save report
          JSONReporter().report(combined, Path("./spring-analysis.json"))

          # Check for critical issues
          critical = [i for i in all_issues if i.severity == Severity.CRITICAL]
          if critical:
              print(f"❌ Found {len(critical)} CRITICAL issues!")
              for issue in critical[:5]:  # Show first 5
                  print(f"  - {issue.description} at {issue.file_path}:{issue.line_number}")
              sys.exit(1)

          print("✅ Spring code quality check passed")
          EOF

      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: spring-analysis-report
          path: spring-analysis.json
```

---

## Best Practices

### Spring Data JPA
1. **Always use @EntityGraph** for associations to avoid N+1
2. **Add pagination** to all list endpoints
3. **Use batch operations** (saveAll, deleteAll) for bulk changes
4. **Mark read-only methods** with `@Transactional(readOnly = true)`
5. **Avoid bidirectional** relationships unless necessary

### Spring Security
1. **Never disable CSRF** in production
2. **Use specific CORS** origins, not wildcards
3. **Load secrets from** environment, not code
4. **Use BCrypt** or Argon2 for passwords
5. **Implement method-level** security with @PreAuthorize

### Spring REST API
1. **Always validate** input with @Valid
2. **Use DTOs** instead of entities
3. **Add pagination** to list endpoints
4. **Follow HTTP semantics** (GET/POST/PUT/DELETE)
5. **Implement proper** error handling with @ControllerAdvice

---

## Example Output

```
================================================================================
  CodePulse Analysis Report - Spring Framework Analyzers
================================================================================
  Directory: /home/user/my-spring-app/src
  Files Analyzed: 156
  Total Lines: 18,450

SUMMARY
--------------------------------------------------------------------------------
  🔴  CRITICAL: 8
  🟠  HIGH:     23
  🟡  MEDIUM:   15
  🟢  LOW:      12
--------------------------------------------------------------------------------
  Total Issues: 58

🔴  CRITICAL ISSUES (8)
================================================================================

  1. CSRF protection disabled
     Location: SecurityConfig.java:42
     Impact: Application vulnerable to Cross-Site Request Forgery attacks
     Solution: Remove .csrf().disable() or implement proper token validation

  2. N+1 Query Problem - Lazy loading in loop
     Location: UserService.java:67
     Impact: 1000 entities = 1001 queries. Can cause 100x performance degradation
     Solution: Use @EntityGraph, JOIN FETCH in query, or batch fetching

  3. CORS allows all origins (*)
     Location: CorsConfig.java:15
     Impact: Any website can make requests to your API, security bypass risk
     Solution: Specify exact allowed origins: .allowedOrigins("https://trusted-domain.com")
```

---

## Additional Resources

- [Spring Data JPA Documentation](https://spring.io/projects/spring-data-jpa)
- [Spring Security Documentation](https://spring.io/projects/spring-security)
- [Spring REST Best Practices](https://spring.io/guides/tutorials/rest/)
- [Hibernate Performance Tuning](https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html#performance)

---

## Next Steps

1. Run analysis on your Spring application
2. Fix CRITICAL and HIGH severity issues first
3. Review MEDIUM issues for optimization opportunities
4. Integrate into your CI/CD pipeline
5. Monitor improvements over time
