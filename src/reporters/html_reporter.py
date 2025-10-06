#!/usr/bin/env python3
"""
HTML Reporter - outputs analysis results as interactive HTML report.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

from core.models import AnalysisResult, Severity


class HTMLReporter:
    """
    Generates interactive HTML reports from analysis results.
    """

    def __init__(self):
        """Initialize HTML reporter."""
        pass

    def report(self, result: AnalysisResult, output_file: Path) -> None:
        """
        Generate HTML report and write to file.

        Args:
            result: AnalysisResult to convert
            output_file: Path to output HTML file
        """
        html = self._generate_html(result)
        self._write_file(html, output_file)

    def _generate_html(self, result: AnalysisResult) -> str:
        """Generate complete HTML document."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodePulse Analysis Report</title>
    {self._get_styles()}
</head>
<body>
    <div class="container">
        {self._generate_header(result)}
        {self._generate_summary(result)}
        {self._generate_issues(result)}
        {self._generate_footer()}
    </div>
    {self._get_scripts()}
</body>
</html>"""

    def _generate_header(self, result: AnalysisResult) -> str:
        """Generate report header."""
        analyzer = result.metadata.get('analyzer', 'CodePulse')
        directory = result.metadata.get('directory', 'N/A')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""
        <header>
            <h1>🔍 CodePulse Analysis Report</h1>
            <div class="meta">
                <p><strong>Analyzer:</strong> {analyzer}</p>
                <p><strong>Directory:</strong> {directory}</p>
                <p><strong>Generated:</strong> {timestamp}</p>
                <p><strong>Files Analyzed:</strong> {result.files_analyzed}</p>
                <p><strong>Lines of Code:</strong> {result.total_lines:,}</p>
            </div>
        </header>"""

    def _generate_summary(self, result: AnalysisResult) -> str:
        """Generate summary section."""
        critical = len(result.get_issues_by_severity(Severity.CRITICAL))
        high = len(result.get_issues_by_severity(Severity.HIGH))
        medium = len(result.get_issues_by_severity(Severity.MEDIUM))
        low = len(result.get_issues_by_severity(Severity.LOW))
        total = len(result.issues)

        return f"""
        <section class="summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-card critical">
                    <div class="number">{critical}</div>
                    <div class="label">🔴 Critical</div>
                </div>
                <div class="summary-card high">
                    <div class="number">{high}</div>
                    <div class="label">🟠 High</div>
                </div>
                <div class="summary-card medium">
                    <div class="number">{medium}</div>
                    <div class="label">🟡 Medium</div>
                </div>
                <div class="summary-card low">
                    <div class="number">{low}</div>
                    <div class="label">🟢 Low</div>
                </div>
            </div>
            <div class="total-issues">
                Total Issues: <strong>{total}</strong>
            </div>
        </section>"""

    def _generate_issues(self, result: AnalysisResult) -> str:
        """Generate issues section."""
        html = '<section class="issues"><h2>Issues Details</h2>'

        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
            issues = result.get_issues_by_severity(severity)
            if not issues:
                continue

            html += f'<h3>{severity.emoji} {severity.value} ({len(issues)})</h3>'
            html += '<div class="issues-list">'

            for issue in issues:
                html += self._generate_issue_card(issue)

            html += '</div>'

        html += '</section>'
        return html

    def _generate_issue_card(self, issue) -> str:
        """Generate HTML for a single issue."""
        severity_class = str(issue.severity).lower()
        code_snippet = issue.code_snippet.replace('<', '&lt;').replace('>', '&gt;')

        return f"""
        <div class="issue-card {severity_class}">
            <div class="issue-header">
                <h4>{issue.description}</h4>
                <span class="severity-badge {severity_class}">{issue.severity_emoji} {issue.severity}</span>
            </div>
            <div class="issue-meta">
                <p><strong>Category:</strong> {issue.category}</p>
                <p><strong>File:</strong> {issue.file_path}:{issue.line_number}</p>
            </div>
            <div class="issue-impact">
                <strong>Impact:</strong> {issue.potential_impact}
            </div>
            {f'<div class="issue-solution"><strong>Solution:</strong> {issue.solution}</div>' if issue.solution else ''}
            {f'<pre class="code-snippet"><code>{code_snippet}</code></pre>' if issue.code_snippet else ''}
        </div>"""

    def _generate_footer(self) -> str:
        """Generate report footer."""
        return """
        <footer>
            <p>Generated by <strong>CodePulse</strong> - Advanced Code Quality Analysis</p>
            <p>Learn more at <a href="https://github.com/yourusername/codepulse">github.com/codepulse</a></p>
        </footer>"""

    def _get_styles(self) -> str:
        """Get CSS styles."""
        return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        header h1 { font-size: 2.5em; margin-bottom: 20px; }
        .meta p { margin: 5px 0; opacity: 0.9; }
        .summary { background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .summary h2 { margin-bottom: 20px; color: #667eea; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .summary-card { padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .summary-card.critical { background: #fee; border-left: 4px solid #e74c3c; }
        .summary-card.high { background: #fff3e0; border-left: 4px solid #f39c12; }
        .summary-card.medium { background: #e3f2fd; border-left: 4px solid #3498db; }
        .summary-card.low { background: #e8f5e9; border-left: 4px solid #27ae60; }
        .summary-card .number { font-size: 3em; font-weight: bold; }
        .summary-card .label { font-size: 1.2em; margin-top: 10px; }
        .total-issues { text-align: center; font-size: 1.3em; margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; }
        .issues { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .issues h2 { color: #667eea; margin-bottom: 20px; }
        .issues h3 { margin: 30px 0 15px 0; color: #555; }
        .issues-list { display: flex; flex-direction: column; gap: 15px; }
        .issue-card { background: #fafafa; border-radius: 8px; padding: 20px; border-left: 4px solid #ddd; }
        .issue-card.critical { border-left-color: #e74c3c; }
        .issue-card.high { border-left-color: #f39c12; }
        .issue-card.medium { border-left-color: #3498db; }
        .issue-card.low { border-left-color: #27ae60; }
        .issue-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px; }
        .issue-header h4 { flex: 1; color: #333; font-size: 1.1em; }
        .severity-badge { padding: 5px 15px; border-radius: 20px; font-size: 0.9em; font-weight: bold; white-space: nowrap; }
        .severity-badge.critical { background: #e74c3c; color: white; }
        .severity-badge.high { background: #f39c12; color: white; }
        .severity-badge.medium { background: #3498db; color: white; }
        .severity-badge.low { background: #27ae60; color: white; }
        .issue-meta { margin-bottom: 10px; color: #666; font-size: 0.95em; }
        .issue-meta p { margin: 3px 0; }
        .issue-impact { background: #fff; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 3px solid #667eea; }
        .issue-solution { background: #e8f5e9; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 3px solid #27ae60; }
        .code-snippet { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 10px; }
        .code-snippet code { font-family: 'Monaco', 'Menlo', 'Consolas', monospace; font-size: 0.9em; }
        footer { text-align: center; margin-top: 40px; padding: 20px; color: #666; font-size: 0.9em; }
        footer a { color: #667eea; text-decoration: none; }
        footer a:hover { text-decoration: underline; }
        @media (max-width: 768px) { .summary-grid { grid-template-columns: 1fr; } }
    </style>"""

    def _get_scripts(self) -> str:
        """Get JavaScript for interactivity."""
        return """
    <script>
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Add filter functionality
        console.log('CodePulse Report loaded successfully');
    </script>"""

    def _write_file(self, html: str, output_file: Path) -> None:
        """Write HTML to file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html, encoding='utf-8')
        print(f"HTML report generated: {output_file}")
