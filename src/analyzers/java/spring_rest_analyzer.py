"""
Spring REST API Analyzer

Detects API design anti-patterns and optimization opportunities in Spring REST applications:
- API design issues
- Missing validation
- Error handling problems
- Performance issues
- DTO vs Entity exposure
- HTTP method misuse
"""

from pathlib import Path
from typing import Dict, Set
from core.models import Pattern, Severity, Category
from core.base_analyzer import BaseAnalyzer


class SpringRestAnalyzer(BaseAnalyzer):
    """Analyzer for Spring REST API anti-patterns and best practices."""

    def __init__(self):
        super().__init__(name="Spring REST API Analyzer")
        self.description = "Detects API design issues and optimization opportunities"

    def get_file_extensions(self) -> Set[str]:
        return {'.java'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        return {
            # Validation Issues
            'missing_valid_annotation': Pattern(
                name='missing_valid_annotation',
                regex=r'@(PostMapping|PutMapping|PatchMapping)[^}]*?@RequestBody(?!\s+@Valid)',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='@RequestBody without @Valid annotation',
                impact='Unvalidated input, potential security risk and data corruption',
                solution='Add @Valid to validate request: @Valid @RequestBody UserRequest request'
            ),

            'entity_in_request': Pattern(
                name='entity_in_request',
                regex=r'@RequestBody\s+\w+Entity\s+',
                severity=Severity.HIGH,
                category=Category.SECURITY,
                description='JPA Entity used directly in @RequestBody',
                impact='Mass assignment vulnerability, tight coupling, over-fetching',
                solution='Create dedicated DTO class for API requests'
            ),

            'entity_in_response': Pattern(
                name='entity_in_response',
                regex=r'(ResponseEntity<|return\s+new\s+ResponseEntity<)\w+Entity>',
                severity=Severity.MEDIUM,
                category=Category.PERFORMANCE,
                description='JPA Entity returned directly in response',
                impact='Lazy loading issues, JSON serialization errors, data exposure',
                solution='Create DTO and use mapper: UserDTO dto = mapper.toDto(entity)'
            ),

            # HTTP Method Misuse
            'get_with_body': Pattern(
                name='get_with_body',
                regex=r'@GetMapping[^}]*?@RequestBody',
                severity=Severity.HIGH,
                category=Category.API_DESIGN,
                description='GET request with @RequestBody',
                impact='Violates HTTP semantics, caching issues, poor API design',
                solution='Use @PostMapping for operations with request body'
            ),

            'delete_returning_body': Pattern(
                name='delete_returning_body',
                regex=r'@DeleteMapping[^}]*?ResponseEntity<(?!Void)',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='DELETE returning response body',
                impact='Non-standard REST practice, client confusion',
                solution='Return ResponseEntity<Void> with 204 No Content for DELETE'
            ),

            'post_not_returning_201': Pattern(
                name='post_not_returning_201',
                regex=r'@PostMapping[^}]*?return\s+ResponseEntity\.ok\(',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='POST returning 200 OK instead of 201 Created',
                impact='Non-standard REST practice',
                solution='Return ResponseEntity.created(location).body(resource) for POST'
            ),

            # Pagination
            'list_without_pagination': Pattern(
                name='list_without_pagination',
                regex=r'@GetMapping[^}]*?List<\w+>\s+get\w+\(\s*\)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='List endpoint without pagination',
                impact='Performance issues with large datasets, potential OOM',
                solution='Add Pageable parameter and return Page<T>: Page<User> getUsers(Pageable pageable)'
            ),

            # Error Handling
            'missing_exception_handler': Pattern(
                name='missing_exception_handler',
                regex=r'@RestController(?!.*@ExceptionHandler)',
                severity=Severity.MEDIUM,
                category=Category.API_DESIGN,
                description='RestController without exception handling',
                impact='Generic error responses, stack traces exposed',
                solution='Add @ExceptionHandler or use @ControllerAdvice for global handling'
            ),

            'generic_exception_catch': Pattern(
                name='generic_exception_catch',
                regex=r'catch\s*\(\s*Exception\s+\w+\s*\)[^}]*?return\s+ResponseEntity',
                severity=Severity.MEDIUM,
                category=Category.API_DESIGN,
                description='Catching generic Exception in controller',
                impact='Loses specific error context, poor error messages',
                solution='Catch specific exceptions and return appropriate status codes'
            ),

            'stacktrace_in_response': Pattern(
                name='stacktrace_in_response',
                regex=r'(e\.printStackTrace|e\.getStackTrace)\(\)[^}]*?ResponseEntity',
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                description='Stack trace included in API response',
                impact='Information disclosure, security vulnerability',
                solution='Log errors server-side, return generic error message to client'
            ),

            # Caching
            'missing_cache_headers': Pattern(
                name='missing_cache_headers',
                regex=r'@GetMapping[^}]*?(?!.*@Cacheable)(?!.*CacheControl)',
                severity=Severity.LOW,
                category=Category.PERFORMANCE,
                description='GET endpoint without cache headers',
                impact='Missed optimization opportunity, increased server load',
                solution='Add @Cacheable or set Cache-Control headers for cacheable resources'
            ),

            # Rate Limiting
            'no_rate_limiting': Pattern(
                name='no_rate_limiting',
                regex=r'@(PostMapping|PutMapping|DeleteMapping).*public(?!.*@RateLimiter)',
                severity=Severity.MEDIUM,
                category=Category.SECURITY,
                description='Public write endpoint without rate limiting',
                impact='Vulnerable to abuse and DoS attacks',
                solution='Add rate limiting: @RateLimiter(name = "api") or use bucket4j'
            ),

            # API Versioning
            'no_api_versioning': Pattern(
                name='no_api_versioning',
                regex=r'@RequestMapping\s*\(\s*"/(api/)?[^v][^"]*"\s*\)',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='API endpoint without versioning',
                impact='Difficult to evolve API without breaking clients',
                solution='Add version to path: @RequestMapping("/api/v1/users")'
            ),

            # Content Negotiation
            'missing_produces': Pattern(
                name='missing_produces',
                regex=r'@(Get|Post|Put)Mapping(?!\s*\([^)]*produces)',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='Mapping without produces declaration',
                impact='Unclear API contract, content negotiation issues',
                solution='Add produces: @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)'
            ),

            # Response Design
            'primitive_response': Pattern(
                name='primitive_response',
                regex=r'@GetMapping[^}]*?(String|Integer|Long|Boolean)\s+get',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='Returning primitive type from API',
                impact='Cannot add metadata later, poor API evolution',
                solution='Wrap in response object: ResponseEntity<UserResponse>'
            ),

            'null_in_response': Pattern(
                name='null_in_response',
                regex=r'return\s+null;[^}]*?@(Get|Post|Put)Mapping',
                severity=Severity.MEDIUM,
                category=Category.API_DESIGN,
                description='Returning null from API endpoint',
                impact='Client-side errors, unclear API contract',
                solution='Return ResponseEntity.notFound() or Optional<T>'
            ),

            # Path Variables
            'missing_path_variable_validation': Pattern(
                name='missing_path_variable_validation',
                regex=r'@PathVariable\s+(?!@Min|@Max|@Pattern)Long\s+id',
                severity=Severity.LOW,
                category=Category.SECURITY,
                description='Path variable without validation',
                impact='Invalid IDs can cause errors or security issues',
                solution='Add validation: @PathVariable @Min(1) Long id'
            ),

            # Request Parameters
            'missing_default_value': Pattern(
                name='missing_default_value',
                regex=r'@RequestParam\s+(?!.*required\s*=\s*false)(?!.*defaultValue)Integer\s+(page|size|limit)',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='Pagination parameter without default value',
                impact='400 error if parameter not provided',
                solution='Add defaultValue: @RequestParam(defaultValue = "0") int page'
            ),

            # Security Headers
            'missing_cors_config': Pattern(
                name='missing_cors_config',
                regex=r'@RestController(?!.*@CrossOrigin)',
                severity=Severity.LOW,
                category=Category.SECURITY,
                description='RestController without CORS configuration',
                impact='CORS errors for browser clients',
                solution='Add @CrossOrigin with specific origins or configure globally'
            ),

            # Documentation
            'missing_api_documentation': Pattern(
                name='missing_api_documentation',
                regex=r'@(Get|Post|Put|Delete)Mapping(?!.*@Operation)(?!.*@ApiOperation)',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='API endpoint without OpenAPI documentation',
                impact='Poor developer experience, no auto-generated docs',
                solution='Add @Operation annotation with description and responses'
            ),

            # HATEOAS
            'missing_links': Pattern(
                name='missing_links',
                regex=r'ResponseEntity<\w+>(?!.*EntityModel)(?!.*RepresentationModel)',
                severity=Severity.LOW,
                category=Category.API_DESIGN,
                description='REST response without HATEOAS links',
                impact='Clients must hardcode URLs, poor REST maturity',
                solution='Use EntityModel<T> and add links for navigation'
            ),

            # Async Operations
            'blocking_in_controller': Pattern(
                name='blocking_in_controller',
                regex=r'@(Get|Post)Mapping[^}]*?\.get\(\)|\.join\(\)',
                severity=Severity.HIGH,
                category=Category.PERFORMANCE,
                description='Blocking operation in controller',
                impact='Thread pool exhaustion, poor scalability',
                solution='Use async: @Async CompletableFuture<T> or return DeferredResult<T>'
            ),
        }


def main():
    """Example usage of Spring REST API Analyzer."""
    import sys
    from reporters.console_reporter import ConsoleReporter

    if len(sys.argv) < 2:
        print("Usage: python spring_rest_analyzer.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    analyzer = SpringRestAnalyzer()
    result = analyzer.analyze_directory(directory)

    reporter = ConsoleReporter(use_colors=True, verbose=True)
    reporter.report(result)


if __name__ == '__main__':
    main()
