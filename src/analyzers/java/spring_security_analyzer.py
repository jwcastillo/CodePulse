"""
Spring Security Analyzer

Detects security anti-patterns and vulnerabilities in Spring Security applications:
- Authentication/Authorization issues
- CSRF protection problems
- Session management issues
- Password encoding weaknesses
- OAuth2/JWT vulnerabilities
- CORS misconfigurations
"""

from pathlib import Path
from typing import Dict, Set
from core.models import Pattern, Severity, Category
from core.base_analyzer import BaseAnalyzer


class SpringSecurityAnalyzer(BaseAnalyzer):
    """Analyzer for Spring Security anti-patterns and vulnerabilities."""

    def __init__(self):
        super().__init__(name="Spring Security Analyzer")
        self.description = "Detects security vulnerabilities in Spring Security configurations"

    def get_file_extensions(self) -> Set[str]:
        return {'.java'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        return {
            # CSRF Protection
            'csrf_disabled': Pattern(
                name='csrf_disabled',
                regex=r'\.csrf\(\)\.disable\(\)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='CSRF protection disabled',
                impact='Application vulnerable to Cross-Site Request Forgery attacks',
                solution='Remove .csrf().disable() or implement proper token validation'
            ),

            # CORS Configuration
            'cors_allow_all': Pattern(
                name='cors_allow_all',
                regex=r'allowedOrigins\s*\(\s*"\*"\s*\)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='CORS allows all origins (*)',
                impact='Any website can make requests to your API, security bypass risk',
                solution='Specify exact allowed origins: .allowedOrigins("https://trusted-domain.com")'
            ),

            'cors_credentials_with_wildcard': Pattern(
                name='cors_credentials_with_wildcard',
                regex=r'allowCredentials\s*\(\s*true\s*\).*allowedOrigins\s*\(\s*"\*"\s*\)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='CORS credentials enabled with wildcard origin',
                impact='Severe security risk - credential theft possible',
                solution='Never use allowCredentials(true) with wildcard origins'
            ),

            # Authentication
            'hardcoded_credentials': Pattern(
                name='hardcoded_credentials',
                regex=r'(password|secret|apiKey)\s*=\s*"[^"]{8,}"',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='Hardcoded credentials in source code',
                impact='Credentials exposed in version control, security breach risk',
                solution='Use environment variables or secure vault: ${PASSWORD}'
            ),

            'weak_password_encoder': Pattern(
                name='weak_password_encoder',
                regex=r'(NoOpPasswordEncoder|StandardPasswordEncoder|Md5PasswordEncoder|ShaPasswordEncoder)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='Weak or deprecated password encoder',
                impact='Passwords easily cracked with rainbow tables or brute force',
                solution='Use BCryptPasswordEncoder or Argon2PasswordEncoder'
            ),

            'password_in_memory': Pattern(
                name='password_in_memory',
                regex=r'inMemoryAuthentication\(\).*\.password\(',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='Passwords stored in memory/code',
                impact='Not suitable for production, credentials in source code',
                solution='Use database or LDAP authentication for production'
            ),

            # Authorization
            'permit_all_endpoints': Pattern(
                name='permit_all_endpoints',
                regex=r'authorizeRequests\(\).*\.anyRequest\(\)\.permitAll\(\)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='All endpoints permit unrestricted access',
                impact='No authentication required, complete security bypass',
                solution='Use .authenticated() or role-based access control'
            ),

            'missing_method_security': Pattern(
                name='missing_method_security',
                regex=r'@RestController(?!.*@PreAuthorize)(?!.*@Secured)',
                severity=Severity.MEDIUM,
                category=Category.SECURITY,
                description='Controller without method-level security',
                impact='Relying only on URL-based security, easier to bypass',
                solution='Add @PreAuthorize or @Secured annotations to sensitive methods'
            ),

            'antmatchers_too_broad': Pattern(
                name='antmatchers_too_broad',
                regex=r'\.antMatchers\s*\(\s*"/\*\*"\s*\)\.permitAll\(\)',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='Overly broad antMatcher pattern',
                impact='May unintentionally expose protected endpoints',
                solution='Use specific paths: .antMatchers("/public/**", "/health").permitAll()'
            ),

            # Session Management
            'session_fixation_none': Pattern(
                name='session_fixation_none',
                regex=r'sessionFixation\(\)\.none\(\)',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='Session fixation protection disabled',
                impact='Vulnerable to session fixation attacks',
                solution='Use .sessionFixation().migrateSession() or .newSession()'
            ),

            'unlimited_sessions': Pattern(
                name='unlimited_sessions',
                regex=r'sessionCreationPolicy\s*\(\s*SessionCreationPolicy\.ALWAYS\s*\)',
                severity=Severity.MEDIUM,
                category=Category.SECURITY,
                description='No session limit configured',
                impact='Users can create unlimited sessions, potential DoS',
                solution='Configure .maximumSessions(1) for concurrent session control'
            ),

            # OAuth2/JWT
            'weak_jwt_algorithm': Pattern(
                name='weak_jwt_algorithm',
                regex=r'Algorithm\.(HMAC256|HS256)\s*\(\s*"[^"]{1,15}"\s*\)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='Weak JWT signing key (less than 256 bits)',
                impact='JWT tokens can be forged, complete authentication bypass',
                solution='Use strong secret (32+ characters) or RS256 with key pairs'
            ),

            'jwt_no_expiration': Pattern(
                name='jwt_no_expiration',
                regex=r'JWT\.create\(\)(?!.*withExpiresAt)',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='JWT token without expiration',
                impact='Tokens valid forever, cannot revoke compromised tokens',
                solution='Add .withExpiresAt(expirationTime) to JWT builder'
            ),

            'jwt_secret_in_code': Pattern(
                name='jwt_secret_in_code',
                regex=r'jwt\.secret\s*=\s*"[^"]+"|signWith\([^)]*"[^"]{20,}"',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='JWT secret hardcoded in source code',
                impact='Anyone with code access can forge tokens',
                solution='Load secret from environment: System.getenv("JWT_SECRET")'
            ),

            # SSL/TLS
            'disable_ssl_verification': Pattern(
                name='disable_ssl_verification',
                regex=r'(setSSLHostnameVerifier.*ALLOW_ALL|TrustManager.*checkServerTrusted\s*\(\s*\)\s*\{)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='SSL certificate verification disabled',
                impact='Vulnerable to man-in-the-middle attacks',
                solution='Never disable SSL verification in production'
            ),

            # Headers
            'missing_security_headers': Pattern(
                name='missing_security_headers',
                regex=r'http\.headers\(\)(?!.*contentSecurityPolicy)(?!.*frameOptions)',
                severity=Severity.MEDIUM,
                category=Category.SECURITY,
                description='Missing security headers configuration',
                impact='Vulnerable to clickjacking, XSS, and other attacks',
                solution='Add .headers().contentSecurityPolicy(), .frameOptions().deny()'
            ),

            'x_frame_options_disabled': Pattern(
                name='x_frame_options_disabled',
                regex=r'frameOptions\(\)\.disable\(\)',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='X-Frame-Options header disabled',
                impact='Vulnerable to clickjacking attacks',
                solution='Use .frameOptions().deny() or .sameOrigin()'
            ),

            # Input Validation
            'sql_injection_risk': Pattern(
                name='sql_injection_risk',
                regex=r'(entityManager\.createQuery|jdbcTemplate\.query)\s*\([^)]*\+',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='Potential SQL injection - string concatenation in query',
                impact='Database compromise, data theft, data manipulation',
                solution='Use parameterized queries or prepared statements'
            ),

            'path_traversal_risk': Pattern(
                name='path_traversal_risk',
                regex=r'new\s+File\s*\([^)]*request\.(getParameter|getPathVariable)',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='Potential path traversal vulnerability',
                impact='Unauthorized file access, reading sensitive files',
                solution='Validate and sanitize file paths, use whitelist approach'
            ),

            # Logging Security Issues
            'logging_sensitive_data': Pattern(
                name='logging_sensitive_data',
                regex=r'log\.(info|debug|trace)\([^)]*(password|token|secret|apiKey)',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='Logging sensitive data',
                impact='Credentials exposed in log files',
                solution='Never log passwords, tokens, or secrets. Mask sensitive data'
            ),
        }


def main():
    """Example usage of Spring Security Analyzer."""
    import sys
    from reporters.console_reporter import ConsoleReporter

    if len(sys.argv) < 2:
        print("Usage: python spring_security_analyzer.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    analyzer = SpringSecurityAnalyzer()
    result = analyzer.analyze_directory(directory)

    reporter = ConsoleReporter(use_colors=True, verbose=True)
    reporter.report(result)


if __name__ == '__main__':
    main()
