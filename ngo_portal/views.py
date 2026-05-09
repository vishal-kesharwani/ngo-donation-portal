from __future__ import annotations

import html
from typing import Any, Dict, Optional

from .formatters import format_money
from .security_content import control_rows
from .services import donation_totals, recent_events, recent_failed_login_total


def nav_html(session: Optional[Dict[str, Any]]) -> str:
    if not session:
        return "\n".join(
            [
                '<a href="/" class="nav-link">Overview</a>',
                '<a href="/login" class="nav-link">Sign in</a>',
            ]
        )

    items = ['<a href="/" class="nav-link">Overview</a>']
    if session["role"] == "admin":
        items.append('<a href="/admin/dashboard" class="nav-link active">Operations</a>')
    else:
        items.append('<a href="/dashboard" class="nav-link active">My Giving</a>')
        items.append('<a href="/donate" class="nav-link">New Donation</a>')
    items.append(
        f"""
        <form method="post" action="/logout" class="inline-form">
            <input type="hidden" name="csrf" value="{html.escape(session['csrf'])}">
            <button type="submit" class="nav-button">Sign out</button>
        </form>
        """
    )
    items.append(f'<span class="user-chip">{html.escape(session["name"])}</span>')
    return "\n".join(items)


def page_shell(title: str, session: Optional[Dict[str, Any]], content: str, notice: Optional[str] = None, error: Optional[str] = None) -> str:
    notice_html = f'<div class="alert alert-success">{html.escape(notice)}</div>' if notice else ""
    error_html = f'<div class="alert alert-error">{html.escape(error)}</div>' if error else ""
    if not session:
        return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
<header class="site-header">
    <a class="site-brand" href="/">
        <span class="site-mark">VK</span>
        <span>
            <strong>ImpactOps</strong>
            <small>Donor Management Platform</small>
        </span>
    </a>
    <nav class="site-nav">
        <a href="#platform">Platform</a>
        <a href="#security">Security</a>
        <a href="#operations">Operations</a>
        <a class="site-login" href="/login">Portal sign in</a>
    </nav>
</header>
<main class="site-main">
    {notice_html}
    {error_html}
    {content}
</main>
<footer class="site-footer">
    <span>ImpactOps for vishalkesharwani.in</span>
    <span>Secure donor operations | Auditable workflows | Private access</span>
</footer>
</body>
</html>"""

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
<div class="app-shell">
    <aside class="sidebar">
        <div class="brand-block">
            <div class="brand-mark">IO</div>
            <div>
                <div class="brand-title">ImpactOps</div>
                <div class="brand-subtitle">Operations Portal</div>
            </div>
        </div>
        <nav class="nav">{nav_html(session)}</nav>
    </aside>
    <section class="workspace">
        <main class="content">
            {notice_html}
            {error_html}
            {content}
        </main>
        <footer class="footer">portal.vishalkesharwani.in | Protected workspace for authorized operations users.</footer>
    </section>
</div>
</body>
</html>"""


def home_page(session: Optional[Dict[str, Any]]) -> str:
    total_count, total_amount = donation_totals()
    if not session:
        content = f"""
        <section class="site-hero">
            <div class="hero-copy">
                <p class="eyebrow">Hosted donor operations portal</p>
                <h1>Clean, secure donation management for modern social impact teams.</h1>
                <p class="lead">ImpactOps centralizes donor records, contribution entry, operational review, and access monitoring in a focused web portal ready for deployment under your own domain.</p>
                <div class="site-actions">
                    <a class="btn btn-primary" href="/login">Open secure portal</a>
                    <a class="btn btn-secondary" href="#platform">View platform</a>
                </div>
            </div>
            <div class="hero-panel">
                <div class="panel-topline">
                    <span>Live workspace snapshot</span>
                    <strong>Protected</strong>
                </div>
                <div class="hero-metric"><span>Donation records</span><strong>{total_count}</strong></div>
                <div class="hero-metric"><span>Total recorded value</span><strong>{format_money(total_amount)}</strong></div>
                <div class="mini-ledger">
                    <div><span>Access control</span><strong>Role based</strong></div>
                    <div><span>Audit stream</span><strong>Enabled</strong></div>
                    <div><span>Submission safety</span><strong>Validated</strong></div>
                </div>
            </div>
        </section>
        <section id="platform" class="site-section">
            <div class="section-heading">
                <p class="eyebrow">Platform</p>
                <h2>Built around the daily work of donation teams.</h2>
            </div>
            <div class="feature-grid">
                <article class="feature-card"><h3>Donation ledger</h3><p>Record contributions with donor identity, amount, program allocation, status, and timestamped ownership.</p></article>
                <article class="feature-card"><h3>Operations review</h3><p>Give administrators a concise workspace for recent records, totals, access attempts, and activity trails.</p></article>
                <article class="feature-card"><h3>Donor workspace</h3><p>Let authenticated donors view their own contribution history and submit new records through a guided form.</p></article>
            </div>
        </section>
        <section id="security" class="site-section security-band">
            <div>
                <p class="eyebrow">Security by default</p>
                <h2>Private access, validated transactions, and audit visibility.</h2>
            </div>
            <div class="security-list">
                <span>Signed sessions</span>
                <span>Role-based access</span>
                <span>CSRF validation</span>
                <span>Parameterized queries</span>
                <span>Login throttling</span>
                <span>Security headers</span>
            </div>
        </section>
        <section id="operations" class="site-section split-feature">
            <div>
                <p class="eyebrow">Deployment ready</p>
                <h2>Designed for a subdomain like portal.vishalkesharwani.in.</h2>
                <p class="lead">The app uses a simple Python entrypoint, isolated modules, persistent SQLite storage, and clean public/portal separation so it can be hosted behind HTTPS on a VPS or cloud instance.</p>
            </div>
            <div class="deploy-card">
                <span>Suggested route</span>
                <strong>portal.vishalkesharwani.in</strong>
                <p>Reverse proxy -> Python WSGI app -> private data directory</p>
            </div>
        </section>
        """
        return page_shell("ImpactOps - Donor Management Platform", session, content)

    primary_href = "/admin/dashboard" if session and session.get("role") == "admin" else "/donate" if session else "/login"
    primary_text = "Open Operations" if session and session.get("role") == "admin" else "Record Donation" if session else "Sign in"
    content = f"""
    <section class="page-header">
        <div>
            <p class="eyebrow">Workspace overview</p>
            <h1>Manage donation activity from one protected workspace.</h1>
            <p class="lead">Review totals, record contributions, and monitor operational activity with access scoped to your assigned role.</p>
        </div>
        <a class="btn btn-primary" href="{primary_href}">{primary_text}</a>
    </section>
    <section class="metric-grid">
        <div class="metric-card"><span class="metric-label">Total donations</span><strong>{total_count}</strong></div>
        <div class="metric-card"><span class="metric-label">Recorded value</span><strong>{format_money(total_amount)}</strong></div>
        <div class="metric-card"><span class="metric-label">Access model</span><strong>RBAC</strong></div>
        <div class="metric-card"><span class="metric-label">Audit status</span><strong>Active</strong></div>
    </section>
    <section class="split-layout">
        <div class="panel">
            <h2>Workspace Controls</h2>
            <div class="control-list">
                <div><span>Authentication</span><strong>Signed session cookies</strong></div>
                <div><span>Authorization</span><strong>Donor and admin roles</strong></div>
                <div><span>Transaction safety</span><strong>CSRF and input validation</strong></div>
                <div><span>Monitoring</span><strong>Audit event stream</strong></div>
            </div>
        </div>
        <div class="panel">
            <h2>Operational Workflow</h2>
            <ol class="workflow">
                <li>Sign in with an assigned account.</li>
                <li>Record or review donation activity.</li>
                <li>Administrators monitor access events and rejected requests.</li>
                <li>Security-relevant activity remains available for review.</li>
            </ol>
        </div>
    </section>
    """
    return page_shell("ImpactOps Workspace", session, content)


def login_page(session: Optional[Dict[str, Any]], error: Optional[str] = None) -> str:
    content = """
    <section class="auth-layout">
        <div class="auth-copy">
            <p class="eyebrow">Secure portal</p>
            <h1>Access your ImpactOps workspace.</h1>
            <p class="lead">Sign in to manage donation records, review operational activity, and work inside a protected donor-management environment.</p>
        </div>
        <div class="panel form-panel">
            <form method="post" action="/login">
                <div class="field">
                    <label for="email">Work email</label>
                    <input id="email" name="email" type="email" autocomplete="username" required>
                </div>
                <div class="field">
                    <label for="password">Password</label>
                    <input id="password" name="password" type="password" autocomplete="current-password" required>
                </div>
                <button class="btn btn-primary btn-wide" type="submit">Sign in</button>
            </form>
        </div>
    </section>
    """
    return page_shell("Sign in - ImpactOps", session, content, error=error)


def donate_page(session: Optional[Dict[str, Any]], error: Optional[str] = None, notice: Optional[str] = None) -> str:
    if not session:
        return page_shell(
            "Record Donation - ImpactOps",
            session,
            """
            <section class="empty-state">
                <h1>Sign in required</h1>
                <p>Donation entry is available only to authenticated users.</p>
                <a class="btn btn-primary" href="/login">Sign in</a>
            </section>
            """,
            error=error,
            notice=notice,
        )

    donor_name = html.escape(session["name"])
    donor_email = html.escape(session["email"])
    csrf = html.escape(session["csrf"])
    content = f"""
    <section class="page-header compact">
        <div>
            <p class="eyebrow">Donation entry</p>
            <h1>Record a contribution</h1>
            <p class="lead">Validated records are written to the donation ledger and linked to the authenticated user.</p>
        </div>
    </section>
    <section class="panel form-panel wide">
        <form method="post" action="/donate">
            <input type="hidden" name="csrf" value="{csrf}">
            <div class="form-grid">
                <div class="field"><label for="donor_name">Donor name</label><input id="donor_name" name="donor_name" type="text" value="{donor_name}" required></div>
                <div class="field"><label for="donor_email">Donor email</label><input id="donor_email" name="donor_email" type="email" value="{donor_email}" required></div>
                <div class="field"><label for="amount">Amount</label><input id="amount" name="amount" type="number" min="1" step="1" placeholder="1500" required></div>
                <div class="field"><label for="purpose">Program allocation</label><input id="purpose" name="purpose" type="text" placeholder="Education support" required></div>
            </div>
            <div class="form-actions"><button class="btn btn-primary" type="submit">Save donation</button></div>
        </form>
    </section>
    """
    return page_shell("Record Donation - ImpactOps", session, content, error=error, notice=notice)


def dashboard_page(session: Dict[str, Any], donations: list[Any], is_admin: bool = False) -> str:
    total_count, total_amount = donation_totals()
    failed_logins = recent_failed_login_total() if is_admin else 0
    recent = recent_events(8) if is_admin else []
    heading = "Operations Center" if is_admin else "My Contributions"
    subtitle = "Donation ledger, access activity, and operating metrics" if is_admin else "Your recorded contribution history"
    action_html = "" if is_admin else '<a class="btn btn-primary" href="/donate">Record donation</a>'

    rows = "".join(
        f"""
        <tr>
            <td>{row['id']}</td>
            <td>{html.escape(row['donor_name'])}</td>
            <td>{html.escape(row['donor_email'])}</td>
            <td>{format_money(float(row['amount']))}</td>
            <td>{html.escape(row['purpose'])}</td>
            <td><span class="status-pill">{html.escape(row['status'])}</span></td>
        </tr>
        """
        for row in donations
    ) or '<tr><td colspan="6" class="muted">No donation records found.</td></tr>'

    content = f"""
    <section class="page-header compact">
        <div>
            <p class="eyebrow">{heading}</p>
            <h1>{html.escape(subtitle)}</h1>
            <p class="lead">Signed in as {html.escape(session['email'])}</p>
        </div>
        {action_html}
    </section>
    <section class="metric-grid">
        <div class="metric-card"><span class="metric-label">Donation records</span><strong>{total_count}</strong></div>
        <div class="metric-card"><span class="metric-label">Total value</span><strong>{format_money(total_amount)}</strong></div>
        <div class="metric-card"><span class="metric-label">Failed logins</span><strong>{failed_logins}</strong></div>
        <div class="metric-card"><span class="metric-label">Policy controls</span><strong>{len(control_rows())}</strong></div>
    </section>
    <section class="panel">
        <div class="table-header"><h2>Donation Ledger</h2><span>{len(donations)} latest records</span></div>
        <div class="table-wrap"><table>
            <thead><tr><th>ID</th><th>Donor</th><th>Email</th><th>Amount</th><th>Program</th><th>Status</th></tr></thead>
            <tbody>{rows}</tbody>
        </table></div>
    </section>
    """

    if is_admin:
        event_rows = "".join(
            f"<tr><td>{html.escape(row['created_at'])}</td><td>{html.escape(row['event_type'])}</td><td>{html.escape(row['details'])}</td><td>{html.escape(row['ip_address'])}</td></tr>"
            for row in recent
        ) or '<tr><td colspan="4" class="muted">No audit events available.</td></tr>'
        content += f"""
        <section class="panel">
            <div class="table-header"><h2>Security Events</h2><span>Latest monitored activity</span></div>
            <div class="table-wrap"><table>
                <thead><tr><th>Timestamp</th><th>Event</th><th>Details</th><th>Source IP</th></tr></thead>
                <tbody>{event_rows}</tbody>
            </table></div>
        </section>
        """

    return page_shell(f"{heading} - ImpactOps", session, content)


def access_denied(session: Optional[Dict[str, Any]], message: str = "Access denied.") -> str:
    content = """
    <section class="empty-state">
        <h1>Access restricted</h1>
        <p>This area is protected by authentication and role-based authorization.</p>
        <div class="button-row">
            <a class="btn btn-primary" href="/login">Sign in</a>
            <a class="btn btn-secondary" href="/">Go to overview</a>
        </div>
    </section>
    """
    return page_shell("Access restricted", session, content, error=message)
