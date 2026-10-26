"""
Security Analyzer

Detects common security issues with regex patterns: hardcoded secrets, injection
(SQL, command), weak cryptography, XSS sinks, disabled TLS verification, insecure
JWT and CORS settings, and unsafe deserialization. Each pattern carries its CWE.

Like the other CodePulse analyzers it is pattern-based: fast and dependency-free,
but it does not track data flow, so treat findings as leads to review.
"""

from pathlib import Path
from typing import Dict, List, Set

from core import BaseAnalyzer, Category, Pattern, Severity

# Dependency, build and VCS folders: scanning them is slow and reports other people's code
EXCLUDED_DIRS = {'node_modules', '.git', 'dist', 'build', 'target', 'out', '.next', '.nuxt', 'vendor',
                 'third-party', 'third_party', 'coverage', '.venv', 'venv', '__pycache__', '.gradle', '.idea'}

# Placeholder values that are not real secrets (e.g. password: "changeme")
_NOT_A_SECRET = r'(?!(?:changeme|change_me|password|example|dummy|test|xxx+|\*+|<[^>]*>|\$\{[^}]*\})["\'])'


class SecurityAnalyzer(BaseAnalyzer):
    """Cross-language security pattern analyzer."""

    def __init__(self):
        super().__init__(name="Security Analyzer")

    def get_file_extensions(self) -> Set[str]:
        return {'.java', '.kt', '.scala', '.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx',
                '.properties', '.yml', '.yaml', '.env', '.json', '.xml'}

    def _scan_files(self, directory: Path) -> List[Path]:
        files = super()._scan_files(directory)
        # minified bundles (*.min.js) are almost always third-party copies, not code the team maintains
        return [f for f in files if not EXCLUDED_DIRS.intersection(f.relative_to(directory).parts[:-1])
                and '.min.' not in f.name]

    def _init_patterns(self) -> Dict[str, Pattern]:
        def p(name, regex, severity, description, impact, solution, cwe):
            return Pattern(name=name, regex=regex, category=Category.SECURITY, severity=severity,
                           description=description, impact=impact, solution=solution, metadata={'cwe': cwe})

        return {
            # --- Secrets
            'aws_access_key': p(
                'aws_access_key', r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b', Severity.CRITICAL,
                'AWS access key ID in source code', 'Account takeover if the key is valid',
                'Revoke the key, load credentials from the environment or a secrets manager', 'CWE-798'),
            'private_key': p(
                'private_key', r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----', Severity.CRITICAL,
                'Private key committed to the repository', 'Impersonation, decryption of traffic or data',
                'Remove it from the repo and its history, rotate the key, store it in a secrets manager', 'CWE-321'),
            'github_token': p(
                'github_token', r'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b', Severity.CRITICAL,
                'GitHub token in source code', 'Repository and organization access with the token scopes',
                'Revoke the token and use CI secrets or the environment', 'CWE-798'),
            'slack_token': p(
                'slack_token', r'\bxox[abposr]-[0-9A-Za-z-]{10,}\b', Severity.HIGH,
                'Slack token in source code', 'Read or post messages as the bot or user',
                'Revoke the token and load it from the environment', 'CWE-798'),
            'hardcoded_secret': p(
                'hardcoded_secret',
                r'(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)'
                r'["\']?\s*[:=]\s*["\']' + _NOT_A_SECRET + r'[^"\'\s]{8,}["\']',
                Severity.HIGH, 'Hardcoded credential', 'Anyone with repo access can use the credential',
                'Read it from the environment or a secrets manager; rotate the exposed value', 'CWE-798'),

            # --- Injection
            'sql_injection_concat': p(
                'sql_injection_concat',
                r'(?:executeQuery|executeUpdate|prepareStatement|createQuery|createNativeQuery|\.execute|\.query)'
                r'\s*\(\s*(?:"[^"\n]*"\s*\+|`[^`\n]*\$\{)',
                Severity.CRITICAL, 'SQL built by string concatenation or template literal',
                'SQL injection: data theft or modification', 'Use bind parameters (?, :name) or a query builder',
                'CWE-89'),
            'command_injection': p(
                'command_injection',
                r'(?:Runtime\.getRuntime\(\)\.exec|new\s+ProcessBuilder|\bexecSync|\bexec)\s*\(\s*'
                r'(?:"[^"\n]*"\s*\+|`[^`\n]*\$\{|[A-Za-z_][\w.]*\s*\+)',
                Severity.CRITICAL, 'Shell command built from concatenated input',
                'Remote command execution', 'Pass arguments as an array (execFile/ProcessBuilder list) and validate input',
                'CWE-78'),
            'eval_usage': p(
                'eval_usage', r'(?<![\w.])eval\s*\(|new\s+Function\s*\(', Severity.HIGH,
                'eval() or new Function() executes dynamic code', 'Code injection if any part comes from input',
                'Remove dynamic evaluation; use JSON.parse or a lookup table', 'CWE-95'),

            # --- XSS sinks
            'dangerously_set_inner_html': p(
                'dangerously_set_inner_html', r'dangerouslySetInnerHTML\s*=\s*\{\{', Severity.MEDIUM,
                'React dangerouslySetInnerHTML', 'Stored or reflected XSS if the HTML is not sanitized',
                'Render text, or sanitize with DOMPurify before injecting', 'CWE-79'),
            'inner_html_assignment': p(
                'inner_html_assignment', r'\.(?:innerHTML|outerHTML)\s*=(?!=)', Severity.MEDIUM,
                'Assignment to innerHTML/outerHTML', 'XSS if the value contains user input',
                'Use textContent, or sanitize the HTML first', 'CWE-79'),

            # --- Cryptography and transport
            'weak_hash': p(
                'weak_hash',
                r'MessageDigest\.getInstance\(\s*"(?:MD5|SHA-?1)"|createHash\(\s*[\'"](?:md5|sha1)[\'"]|DigestUtils\.(?:md5|sha1)',
                Severity.MEDIUM, 'MD5/SHA-1 used for hashing (a problem only for security uses)',
                'Collisions: unsafe for passwords, signatures and tokens; fine for checksums or short ids',
                'For security use SHA-256+ (integrity) or bcrypt/Argon2/PBKDF2 (passwords)', 'CWE-328'),
            'tls_verification_disabled': p(
                'tls_verification_disabled',
                r'rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED["\']?\s*[:=]\s*["\']?0'
                r'|ALLOW_ALL_HOSTNAME_VERIFIER|NoopHostnameVerifier|setHostnameVerifier\(\s*\([^)]*\)\s*->\s*true',
                Severity.HIGH, 'TLS certificate or hostname verification disabled',
                'Man-in-the-middle can read and modify traffic', 'Keep verification on; trust a custom CA if needed',
                'CWE-295'),
            'jwt_none_algorithm': p(
                'jwt_none_algorithm', r'algorithms?\s*:\s*\[?\s*[\'"]none[\'"]', Severity.CRITICAL,
                'JWT accepts the "none" algorithm', 'Unsigned tokens are accepted: authentication bypass',
                'Pin the expected algorithm (e.g. ["RS256"])', 'CWE-347'),
            'cors_wildcard': p(
                'cors_wildcard',
                r'Access-Control-Allow-Origin[\'"]?\s*[,:]\s*[\'"]\*[\'"]|origin\s*:\s*[\'"]\*[\'"]',
                Severity.MEDIUM, 'CORS allows any origin', 'Any site can read responses meant for your users',
                'Allow a list of known origins', 'CWE-942'),

            # --- Deserialization
            'java_deserialization': p(
                'java_deserialization', r'new\s+ObjectInputStream\s*\(', Severity.MEDIUM,
                'Java native deserialization (ObjectInputStream)', 'Remote code execution with untrusted data (gadget chains)',
                'Avoid native serialization for untrusted input; use JSON, or an ObjectInputFilter allowlist', 'CWE-502'),
        }
