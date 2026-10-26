"""SecurityAnalyzer: every pattern fires on a vulnerable sample and stays quiet on the safe version."""
import pytest

from analyzers.security import SecurityAnalyzer

# (pattern, file, vulnerable code, safe code)
CASES = [
    ("aws_access_key", "Config.java", 'String k = "AKIAIOSFODNN7EXAMPLE";', 'String k = System.getenv("AWS_ACCESS_KEY_ID");'),
    ("private_key", "deploy.yml", "key: |\n  -----BEGIN RSA PRIVATE KEY-----\n  MIIE...", "key: ${DEPLOY_KEY}"),
    ("github_token", "ci.js", 'const t = "ghp_' + "a" * 36 + '";', "const t = process.env.GITHUB_TOKEN;"),
    ("slack_token", "notify.ts", 'const s = "xoxb-123456789012-abcdefghij";', "const s = process.env.SLACK_TOKEN;"),
    ("hardcoded_secret", "application.properties", 'db.password="S3cr3tPassw0rd!"', "db.password=${DB_PASSWORD}"),
    ("hardcoded_secret", "app.js", "const apiKey = 'k_live_9f8e7d6c5b4a';", "const apiKey = 'changeme';"),
    ("sql_injection_concat", "Repo.java", 'stmt.executeQuery("SELECT * FROM users WHERE id = " + id);',
     'stmt.executeQuery("SELECT * FROM users WHERE id = ?");'),
    ("sql_injection_concat", "repo.ts", "db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);",
     "db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);"),
    ("command_injection", "Run.java", 'Runtime.getRuntime().exec("ping " + host);',
     'new ProcessBuilder(List.of("ping", host)).start();'),
    ("command_injection", "run.js", "exec(`convert ${req.query.file} out.png`);", "execFile('convert', [file, 'out.png']);"),
    ("eval_usage", "calc.js", "const r = eval(userInput);", "const r = JSON.parse(userInput);"),
    ("command_injection", "parse.js", "exec(`rm -rf ${dir}`);", "const m = /(\\d+)/.exec(line);"),
    ("dangerously_set_inner_html", "Bio.tsx", "<div dangerouslySetInnerHTML={{ __html: bio }} />", "<div>{bio}</div>"),
    ("inner_html_assignment", "view.js", "el.innerHTML = comment;", "el.textContent = comment;"),
    ("weak_hash", "Hash.java", 'MessageDigest.getInstance("MD5");', 'MessageDigest.getInstance("SHA-256");'),
    ("weak_hash", "hash.js", "crypto.createHash('sha1').update(pw);", "crypto.createHash('sha256').update(data);"),
    ("tls_verification_disabled", "client.js", "https.request({ host, rejectUnauthorized: false });", "https.request({ host, ca });"),
    ("jwt_none_algorithm", "auth.js", "jwt.verify(token, key, { algorithms: ['none'] });", "jwt.verify(token, key, { algorithms: ['RS256'] });"),
    ("cors_wildcard", "server.js", "res.setHeader('Access-Control-Allow-Origin', '*');",
     "res.setHeader('Access-Control-Allow-Origin', 'https://app.example.com');"),
    ("java_deserialization", "Load.java", "Object o = new ObjectInputStream(in).readObject();", "Order o = mapper.readValue(in, Order.class);"),
]


def scan(tmp_path, monkeypatch, name, code):
    (tmp_path / name).write_text(code)
    monkeypatch.chdir(tmp_path)
    result = SecurityAnalyzer().analyze_directory(tmp_path)
    assert "errors" not in result.metadata, result.metadata.get("errors")
    return {i.metadata["pattern"] for i in result.issues}


@pytest.mark.parametrize("pattern,name,bad,good", CASES, ids=[f"{c[0]}:{c[1]}" for c in CASES])
def test_pattern_fires_on_vulnerable_code(tmp_path, monkeypatch, pattern, name, bad, good):
    assert pattern in scan(tmp_path, monkeypatch, name, bad)


@pytest.mark.parametrize("pattern,name,bad,good", CASES, ids=[f"{c[0]}:{c[1]}" for c in CASES])
def test_pattern_is_quiet_on_safe_code(tmp_path, monkeypatch, pattern, name, bad, good):
    assert pattern not in scan(tmp_path, monkeypatch, name, good)


def test_findings_are_security_category_with_cwe(tmp_path, monkeypatch):
    (tmp_path / "a.js").write_text("eval(x);")
    monkeypatch.chdir(tmp_path)
    issue = SecurityAnalyzer().analyze_directory(tmp_path).issues[0]
    assert issue.category.name == "SECURITY" and issue.metadata["cwe"] == "CWE-95"


def test_dependency_and_build_folders_are_skipped(tmp_path, monkeypatch):
    for d in ("node_modules/lib", "target", "static/third-party", "src"):
        (tmp_path / d).mkdir(parents=True)
        (tmp_path / d / "x.js").write_text("eval(x);")
    (tmp_path / "src" / "jquery-2.1.4.min.js").write_text("eval(x);")
    monkeypatch.chdir(tmp_path)
    files = {i.file_path for i in SecurityAnalyzer().analyze_directory(tmp_path).issues}
    assert files == {"src/x.js"}


def test_cli_exposes_security_analyzers():
    import cli
    assert {"security", "spring-security"} <= set(cli.CodePulseCLI.ANALYZERS)
