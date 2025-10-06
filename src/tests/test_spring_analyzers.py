"""
Tests for Spring analyzers (Data JPA, Security, REST API).
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.models import Severity, Category
from analyzers.java.spring_data_analyzer import SpringDataAnalyzer
from analyzers.java.spring_security_analyzer import SpringSecurityAnalyzer
from analyzers.java.spring_rest_analyzer import SpringRestAnalyzer


class TestSpringDataAnalyzer:
    """Tests for Spring Data JPA Analyzer."""

    def test_detects_n_plus_one_lazy_loading(self):
        code = '''
        public class UserService {
            public void processUsers(List<User> users) {
                for (User user : users) {
                    Order order = user.getOrders(); // Lazy loading in loop
                }
            }
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserService.java"
            file_path.write_text(code)

            analyzer = SpringDataAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            assert len(result.issues) > 0
            issue = result.issues[0]
            assert issue.severity == Severity.CRITICAL
            assert 'N+1' in issue.description

    def test_detects_repository_in_loop(self):
        code = '''
        public class OrderService {
            public void loadOrders(List<Long> ids) {
                for (Long id : ids) {
                    Order order = orderRepository.findById(id);
                }
            }
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "OrderService.java"
            file_path.write_text(code)

            analyzer = SpringDataAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            critical = result.get_issues_by_severity(Severity.CRITICAL)
            assert len(critical) > 0
            assert any('Repository' in issue.description for issue in critical)

    def test_detects_save_in_loop(self):
        code = '''
        public class ProductService {
            public void saveProducts(List<Product> products) {
                for (Product product : products) {
                    productRepository.save(product);
                }
            }
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "ProductService.java"
            file_path.write_text(code)

            analyzer = SpringDataAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            high_issues = result.get_issues_by_severity(Severity.HIGH)
            assert len(high_issues) > 0
            assert any('save' in issue.description.lower() for issue in high_issues)

    def test_detects_missing_pagination(self):
        code = '''
        public interface UserRepository extends JpaRepository<User, Long> {
            List<User> findAll();
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserRepository.java"
            file_path.write_text(code)

            analyzer = SpringDataAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            assert len(result.issues) > 0
            assert any('pagination' in issue.description.lower() for issue in result.issues)


class TestSpringSecurityAnalyzer:
    """Tests for Spring Security Analyzer."""

    def test_detects_csrf_disabled(self):
        code = '''
        @Configuration
        public class SecurityConfig {
            public void configure(HttpSecurity http) throws Exception {
                http.csrf().disable();
            }
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "SecurityConfig.java"
            file_path.write_text(code)

            analyzer = SpringSecurityAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            critical = result.get_issues_by_severity(Severity.CRITICAL)
            assert len(critical) > 0
            assert any('CSRF' in issue.description for issue in critical)

    def test_detects_cors_allow_all(self):
        code = '''
        @Configuration
        public class CorsConfig {
            public void configure() {
                config.allowedOrigins("*");
            }
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "CorsConfig.java"
            file_path.write_text(code)

            analyzer = SpringSecurityAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            critical = result.get_issues_by_severity(Severity.CRITICAL)
            assert len(critical) > 0
            assert any('CORS' in issue.description for issue in critical)

    def test_detects_hardcoded_credentials(self):
        code = '''
        public class ApiClient {
            private String apiKey = "sk_live_1234567890abcdef";
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "ApiClient.java"
            file_path.write_text(code)

            analyzer = SpringSecurityAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            critical = result.get_issues_by_severity(Severity.CRITICAL)
            assert len(critical) > 0
            assert any('credential' in issue.description.lower() for issue in critical)

    def test_detects_weak_password_encoder(self):
        code = '''
        @Bean
        public PasswordEncoder passwordEncoder() {
            return NoOpPasswordEncoder.getInstance();
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "SecurityConfig.java"
            file_path.write_text(code)

            analyzer = SpringSecurityAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            critical = result.get_issues_by_severity(Severity.CRITICAL)
            assert len(critical) > 0
            assert any('password' in issue.description.lower() for issue in critical)

    def test_detects_permit_all(self):
        code = '''
        public void configure(HttpSecurity http) {
            http.authorizeRequests().anyRequest().permitAll();
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "SecurityConfig.java"
            file_path.write_text(code)

            analyzer = SpringSecurityAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            critical = result.get_issues_by_severity(Severity.CRITICAL)
            assert len(critical) > 0
            assert any('permit' in issue.description.lower() for issue in critical)


class TestSpringRestAnalyzer:
    """Tests for Spring REST API Analyzer."""

    def test_detects_missing_valid(self):
        code = '''
        @RestController
        public class UserController {
            @PostMapping("/users")
            public ResponseEntity<User> createUser(@RequestBody UserRequest request) {
                return ResponseEntity.ok(userService.create(request));
            }
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserController.java"
            file_path.write_text(code)

            analyzer = SpringRestAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            high_issues = result.get_issues_by_severity(Severity.HIGH)
            assert len(high_issues) > 0
            assert any('@Valid' in issue.description for issue in high_issues)

    def test_detects_entity_in_request(self):
        code = '''
        @PostMapping("/users")
        public User createUser(@RequestBody UserEntity entity) {
            return userService.save(entity);
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserController.java"
            file_path.write_text(code)

            analyzer = SpringRestAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            high_issues = result.get_issues_by_severity(Severity.HIGH)
            assert len(high_issues) > 0
            assert any('Entity' in issue.description for issue in high_issues)

    def test_detects_get_with_body(self):
        code = '''
        @GetMapping("/search")
        public List<User> search(@RequestBody SearchRequest request) {
            return userService.search(request);
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserController.java"
            file_path.write_text(code)

            analyzer = SpringRestAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            high_issues = result.get_issues_by_severity(Severity.HIGH)
            assert len(high_issues) > 0
            assert any('GET' in issue.description for issue in high_issues)

    def test_detects_list_without_pagination(self):
        code = '''
        @GetMapping("/users")
        public List<User> getUsers() {
            return userService.findAll();
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserController.java"
            file_path.write_text(code)

            analyzer = SpringRestAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            high_issues = result.get_issues_by_severity(Severity.HIGH)
            assert len(high_issues) > 0
            assert any('pagination' in issue.description.lower() for issue in high_issues)

    def test_detects_stacktrace_in_response(self):
        code = '''
        @GetMapping("/users/{id}")
        public ResponseEntity<User> getUser(@PathVariable Long id) {
            try {
                return ResponseEntity.ok(userService.find(id));
            } catch (Exception e) {
                e.printStackTrace();
                return ResponseEntity.badRequest().body(null);
            }
        }
        '''
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserController.java"
            file_path.write_text(code)

            analyzer = SpringRestAnalyzer()
            result = analyzer.analyze_directory(Path(tmpdir))

            critical = result.get_issues_by_severity(Severity.CRITICAL)
            assert len(critical) > 0
            assert any('stack' in issue.description.lower() for issue in critical)


class TestSpringAnalyzersIntegration:
    """Integration tests for Spring analyzers."""

    def test_all_analyzers_on_sample_code(self):
        """Test all Spring analyzers on a sample Spring Boot application."""
        code = '''
        @RestController
        @RequestMapping("/api/users")
        public class UserController {
            @Autowired
            private UserRepository userRepository;

            @GetMapping
            public List<User> getAllUsers() {
                return userRepository.findAll(); // Missing pagination
            }

            @PostMapping
            public User createUser(@RequestBody UserEntity user) { // Entity in request, missing @Valid
                return userRepository.save(user);
            }

            @GetMapping("/{id}/orders")
            public List<Order> getUserOrders(@PathVariable Long id) {
                User user = userRepository.findById(id).get();
                List<Order> orders = new ArrayList<>();
                for (Order order : user.getOrders()) { // N+1 lazy loading
                    orders.add(order);
                }
                return orders;
            }
        }

        @Configuration
        public class SecurityConfig {
            public void configure(HttpSecurity http) throws Exception {
                http.csrf().disable() // CSRF disabled
                    .authorizeRequests()
                    .anyRequest().permitAll(); // Permit all
            }
        }
        '''

        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "UserController.java"
            file_path.write_text(code)

            # Run all analyzers
            data_analyzer = SpringDataAnalyzer()
            security_analyzer = SpringSecurityAnalyzer()
            rest_analyzer = SpringRestAnalyzer()

            data_result = data_analyzer.analyze_directory(Path(tmpdir))
            security_result = security_analyzer.analyze_directory(Path(tmpdir))
            rest_result = rest_analyzer.analyze_directory(Path(tmpdir))

            # Should find issues in all categories
            assert len(data_result.issues) > 0
            assert len(security_result.issues) > 0
            assert len(rest_result.issues) > 0

            # Should have critical issues
            all_issues = data_result.issues + security_result.issues + rest_result.issues
            critical = [i for i in all_issues if i.severity == Severity.CRITICAL]
            assert len(critical) >= 2  # At least CSRF and one other


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
