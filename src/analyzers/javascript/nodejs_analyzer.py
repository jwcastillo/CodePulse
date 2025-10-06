#!/usr/bin/env python3
"""
Node.js Code Analyzer - detects anti-patterns and performance issues.

This analyzer focuses on Node.js-specific issues including:
- Event loop blocking operations
- Memory leaks (event listeners, intervals, global variables)
- Promise and async/await anti-patterns
- Stream handling inefficiencies
- Database access patterns
- Security vulnerabilities
"""

from typing import Dict, Set

from core import BaseAnalyzer, Pattern, Category, Severity


class NodeJSAnalyzer(BaseAnalyzer):
    """
    Analyzer for Node.js anti-patterns and best practices.

    Detects common Node.js issues that can impact performance,
    reliability, and security.
    """

    def __init__(self):
        """Initialize the Node.js analyzer."""
        super().__init__(name="Node.js Anti-Pattern Analyzer")

    def get_file_extensions(self) -> Set[str]:
        """Get file extensions for JavaScript/TypeScript files."""
        return {'.js', '.ts', '.mjs', '.cjs'}

    def _init_patterns(self) -> Dict[str, Pattern]:
        """Initialize Node.js-specific detection patterns."""
        return {
            # EVENT LOOP BLOCKING
            'sync_file_operations': Pattern(
                name='sync_file_operations',
                regex=r'fs\.(readFileSync|writeFileSync|readdirSync|existsSync|statSync)',
                category=Category.EVENT_LOOP,
                severity=Severity.CRITICAL,
                description='Synchronous file operation blocks event loop',
                impact='Blocks event loop. Using async versions reduces latency 100x',
                solution='Use fs.promises.readFile() or fs.readFile() with callbacks',
                metadata={
                    'example_bad': 'const data = fs.readFileSync("file.txt")',
                    'example_good': 'const data = await fs.promises.readFile("file.txt")'
                }
            ),

            'sync_crypto': Pattern(
                name='sync_crypto',
                regex=r'crypto\.(pbkdf2Sync|scryptSync|randomBytesSync)',
                category=Category.EVENT_LOOP,
                severity=Severity.CRITICAL,
                description='Synchronous cryptographic operation',
                impact='Blocks event loop completely for 100-500ms',
                solution='Use async versions: crypto.pbkdf2(), crypto.scrypt()',
                metadata={
                    'example_bad': 'const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, "sha512")',
                    'example_good': 'const hash = await crypto.pbkdf2(password, salt, 100000, 64, "sha512")'
                }
            ),

            'json_parse_large': Pattern(
                name='json_parse_large',
                regex=r'JSON\.parse\([^)]*\)',
                category=Category.EVENT_LOOP,
                severity=Severity.MEDIUM,
                description='JSON.parse (can block with large payloads)',
                impact='Blocks event loop with JSON >10MB',
                solution='Use streaming JSON parser or Worker Threads for large JSON',
                metadata={
                    'tips': 'Consider streaming-json-parse for large payloads'
                }
            ),

            # MEMORY LEAKS
            'event_listener_no_cleanup': Pattern(
                name='event_listener_no_cleanup',
                regex=r'\.on\(["\'].*["\'].*\)\s*(?!.*\.removeListener|.*\.off)',
                category=Category.MEMORY,
                severity=Severity.HIGH,
                description='Event listener without cleanup',
                impact='Memory leak: listeners accumulate indefinitely',
                solution='Use .once() or remove with .removeListener() in cleanup',
                metadata={
                    'example_bad': 'emitter.on("event", handler)',
                    'example_good': 'emitter.once("event", handler) // or cleanup with removeListener'
                }
            ),

            'setinterval_no_clear': Pattern(
                name='setinterval_no_clear',
                regex=r'setInterval\(',
                category=Category.MEMORY,
                severity=Severity.HIGH,
                description='setInterval without clearInterval',
                impact='Memory leak if not cleared',
                solution='Store reference and use clearInterval() in cleanup',
                metadata={
                    'example_good': 'const intervalId = setInterval(...);\n// Later: clearInterval(intervalId)'
                }
            ),

            'global_variables': Pattern(
                name='global_variables',
                regex=r'^(var|let|const)\s+\w+\s*=.*(?=\n(?!.*function|.*class|.*\{))',
                category=Category.MEMORY,
                severity=Severity.MEDIUM,
                description='Global variables (scope pollution)',
                impact='Hinders GC, creates potential memory leaks',
                solution='Use ES6 modules or IIFE for local scope',
                metadata={}
            ),

            # PROMISES & ASYNC
            'unhandled_promise': Pattern(
                name='unhandled_promise',
                regex=r'new Promise\([^)]+\)(?!\s*\.(then|catch|finally))',
                category=Category.BEST_PRACTICE,
                severity=Severity.CRITICAL,
                description='Promise without .catch() - unhandled rejection',
                impact='Production crashes, silent errors',
                solution='Always add .catch() or use try/catch with async/await',
                metadata={
                    'example_good': 'promise.catch(err => console.error(err))'
                }
            ),

            'promise_constructor_antipattern': Pattern(
                name='promise_constructor_antipattern',
                regex=r'new Promise\s*\(\s*\([^)]*\)\s*=>\s*\{[^}]*\.(then|catch)',
                category=Category.CODE_SMELL,
                severity=Severity.MEDIUM,
                description='Promise constructor anti-pattern',
                impact='Unnecessarily complex code',
                solution='Already in Promise context, no need for new Promise()',
                metadata={}
            ),

            'async_without_await': Pattern(
                name='async_without_await',
                regex=r'async\s+(?:function|\([^)]*\)\s*=>)\s*\{(?!.*await).*\}',
                category=Category.CODE_SMELL,
                severity=Severity.LOW,
                description='async function without await',
                impact='Unnecessary async, confuses intent',
                solution='Remove async if there is no await',
                metadata={}
            ),

            'callback_hell': Pattern(
                name='callback_hell',
                regex=r'\([^)]*\)\s*=>\s*\{[^}]*\([^)]*\)\s*=>\s*\{[^}]*\([^)]*\)\s*=>\s*\{',
                category=Category.CODE_SMELL,
                severity=Severity.HIGH,
                description='Callback hell (3+ nested levels)',
                impact='Unreadable code, hard to maintain',
                solution='Refactor to async/await or Promises',
                metadata={
                    'example_good': 'Use async/await for sequential operations'
                }
            ),

            # STREAMS
            'large_file_no_stream': Pattern(
                name='large_file_no_stream',
                regex=r'fs\.readFile\([^)]*\.(csv|log|json|txt)',
                category=Category.MEMORY,
                severity=Severity.HIGH,
                description='Reading large file without streams',
                impact='Loads entire file in memory. 1GB file = 1GB RAM',
                solution='Use fs.createReadStream() for files >100MB',
                metadata={
                    'example_good': 'const stream = fs.createReadStream("large.csv")'
                }
            ),

            'buffer_concat_loop': Pattern(
                name='buffer_concat_loop',
                regex=r'(for|while).*Buffer\.concat',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='Buffer.concat in loop',
                impact='O(N²) performance, very slow',
                solution='Collect buffers in array, concat once at the end',
                metadata={
                    'example_good': 'const buffers = []; ... Buffer.concat(buffers)'
                }
            ),

            # DATABASE
            'query_in_loop': Pattern(
                name='query_in_loop',
                regex=r'(for|while)\s*\([^)]+\)\s*\{[^}]*(query|findOne|findById|execute)',
                category=Category.DATABASE,
                severity=Severity.CRITICAL,
                description='N+1 Query Problem',
                impact='N+1 queries. 1000 items = 1001 queries instead of 2',
                solution='Use findMany/findAll with array of IDs',
                metadata={
                    'example_bad': 'for(const id of ids) { await findById(id) }',
                    'example_good': 'const results = await findByIds(ids)'
                }
            ),

            'no_connection_pool': Pattern(
                name='no_connection_pool',
                regex=r'mysql\.createConnection|pg\.Client\(',
                category=Category.DATABASE,
                severity=Severity.CRITICAL,
                description='Direct DB connection without pool',
                impact='Exhausts DB connections, 10-100x slower',
                solution='Use connection pool: createPool() or use ORM like Prisma',
                metadata={
                    'example_good': 'const pool = mysql.createPool({ ... })'
                }
            ),

            'select_star': Pattern(
                name='select_star',
                regex=r'SELECT\s+\*\s+FROM',
                category=Category.DATABASE,
                severity=Severity.MEDIUM,
                description='SELECT * (fetching all columns)',
                impact='Unnecessary network/memory overhead',
                solution='Select only needed columns',
                metadata={}
            ),

            # ERROR HANDLING
            'try_without_finally': Pattern(
                name='try_without_finally',
                regex=r'try\s*\{[^}]*\}\s*catch[^}]*\}(?!\s*finally)',
                category=Category.BEST_PRACTICE,
                severity=Severity.MEDIUM,
                description='try/catch without finally for cleanup',
                impact='Resource leaks (connections, files)',
                solution='Add finally block to close resources',
                metadata={}
            ),

            'empty_catch': Pattern(
                name='empty_catch',
                regex=r'catch\s*\([^)]*\)\s*\{\s*\}',
                category=Category.BEST_PRACTICE,
                severity=Severity.CRITICAL,
                description='Empty catch block (swallowing errors)',
                impact='Silent errors, impossible debugging',
                solution='Log error or re-throw with context',
                metadata={
                    'example_good': 'catch(err) { logger.error(err); throw err; }'
                }
            ),

            # SECURITY
            'eval_usage': Pattern(
                name='eval_usage',
                regex=r'\beval\s*\(',
                category=Category.SECURITY,
                severity=Severity.CRITICAL,
                description='Using eval() - security vulnerability',
                impact='Code injection, XSS, RCE',
                solution='NEVER use eval. Find alternatives',
                metadata={}
            ),

            'sql_concatenation': Pattern(
                name='sql_concatenation',
                regex=r'(query|execute)\s*\([^)]*\+\s*\w+',
                category=Category.SECURITY,
                severity=Severity.CRITICAL,
                description='SQL concatenation - SQL Injection risk',
                impact='SQL Injection vulnerability',
                solution='Use prepared statements or ORMs',
                metadata={
                    'example_good': 'query("SELECT * FROM users WHERE id = ?", [userId])'
                }
            ),

            'process_env_no_validation': Pattern(
                name='process_env_no_validation',
                regex=r'process\.env\.\w+',
                category=Category.SECURITY,
                severity=Severity.MEDIUM,
                description='Environment variables without validation',
                impact='Runtime errors if variable does not exist',
                solution='Validate with zod or similar at startup',
                metadata={
                    'example_good': 'const env = z.object({ PORT: z.string() }).parse(process.env)'
                }
            ),

            # PERFORMANCE
            'regex_in_loop': Pattern(
                name='regex_in_loop',
                regex=r'(for|while).*new RegExp|\.match\(\/.*\/',
                category=Category.PERFORMANCE,
                severity=Severity.HIGH,
                description='Regex compilation in loop',
                impact='Compiles regex thousands of times',
                solution='Compile regex outside the loop',
                metadata={
                    'example_good': 'const regex = /pattern/; for(...) { regex.test(str) }'
                }
            ),

            'object_in_loop': Pattern(
                name='object_in_loop',
                regex=r'(for|while).*new Object|new Array|\{\}|\[\]',
                category=Category.PERFORMANCE,
                severity=Severity.MEDIUM,
                description='Object allocation in loop',
                impact='High GC pressure',
                solution='Reuse objects or create outside loop',
                metadata={}
            ),

            # WORKER THREADS
            'cpu_intensive_no_worker': Pattern(
                name='cpu_intensive_no_worker',
                regex=r'(for.*for.*for|crypto\.(pbkdf2|scrypt)|JSON\.parse.*large)',
                category=Category.CONCURRENCY,
                severity=Severity.HIGH,
                description='CPU-intensive operation in main thread',
                impact='Blocks event loop completely',
                solution='Use Worker Threads for CPU-intensive tasks',
                metadata={
                    'example_good': 'const { Worker } = require("worker_threads");\nconst worker = new Worker("./heavy-compute.js")'
                }
            ),
        }
