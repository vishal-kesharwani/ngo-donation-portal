# Final Review 3 PPT Content - NGO Donation Portal Cybersecurity Case Study

## Slide 1: Title
- Secure NGO Donation Portal
- Cybersecurity Case Study Implementation - Final Review
- Focus: Integration, hardening, cloud security, AI/ML discussion, and viva readiness

## Slide 2: Project Problem Statement
- NGOs collect donor data and payment-related donation records through web portals.
- The system must prevent unauthorized access, tampering, injection attacks, CSRF, brute-force login attempts, and data exposure.
- Goal: build a secure demo portal and validate security controls through testing and monitoring.

## Slide 3: System Scope
- Donor login
- Donation form submission
- Donor dashboard
- Admin dashboard
- Audit log monitoring
- Security hardening and risk tracking
- Conceptual cloud and AI/ML security extension

## Slide 4: Review 1 Recap - Threat Analysis
- STRIDE threats considered: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege.
- Main risks: SQL injection, broken access control, CSRF, weak authentication, brute-force login, sensitive data exposure.
- Risk mitigation planned using authentication, RBAC, validation, encryption in transit, logging, and secure deployment controls.

## Slide 5: Review 2 Recap - Implementation
- Implemented Python WSGI web app with SQLite database.
- Added donor and admin roles.
- Added signed session cookie authentication.
- Added server-side input validation.
- Added CSRF protection for donation and logout.
- Added audit logging for login, access denial, CSRF, and donation events.

## Slide 6: Final Review 3 Enhancements
- Added integrated hardening page for final review evidence.
- Added security response headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, Cache-Control.
- Added login brute-force throttling using failed login tracking.
- Added admin dashboard monitoring metrics.
- Added cloud and AI/ML cybersecurity discussion page.

## Slide 7: Secure Architecture
- User browser connects to the NGO portal over HTTPS.
- Application layer handles authentication, authorization, validation, and CSRF checks.
- Database stores users, donations, login attempts, and audit logs.
- Admin dashboard provides monitoring and incident evidence.
- In production, firewall/WAF and private database networking protect the deployment.

## Slide 8: Implemented Security Controls
- Authentication: PBKDF2 password hashing and signed sessions.
- Authorization: donor/admin role-based access control.
- Input validation: strict validation for email, name, amount, and purpose.
- Injection protection: parameterized SQLite queries.
- CSRF defense: session-bound tokens.
- Monitoring: security audit logs.
- Hardening: secure browser headers and cookie controls.

## Slide 9: Security Testing and Validation
- Authentication testing: valid login, invalid login, failed login logging.
- Authorization testing: donor blocked from admin dashboard.
- Input validation testing: invalid donation payload rejected.
- CSRF testing: missing/wrong token blocked.
- API testing: admin-only summary endpoint protected.
- Before/after evidence: attacks produce safe error responses and audit events.

## Slide 10: Tool Usage and Interpretation
- Nmap: verifies exposed ports and confirms only expected service is open in the test environment.
- Wireshark: demonstrates traffic observation and explains need for HTTPS/TLS in deployment.
- OWASP ZAP or Burp Suite: can be used to check headers, forms, and basic web vulnerabilities.
- SQLite inspection: verifies stored donations and audit events.

## Slide 11: Risk Assessment After Mitigation
- SQL injection: High to Low through parameterized queries.
- Broken access control: High to Low through RBAC checks.
- CSRF: Medium to Low through CSRF token validation.
- Brute-force login: Medium to Medium through throttling.
- Session theft: High to Medium; production requires HTTPS and secret rotation.
- Sensitive data exposure: High to Medium through least privilege and no-store headers.

## Slide 12: System Hardening
- Firewall: expose only HTTP/HTTPS through reverse proxy; keep database private.
- Secure configuration: use strong secret key from environment variable.
- Patch management: update runtime and dependencies regularly.
- Logging and monitoring: review audit events for suspicious behavior.
- Backup and recovery: encrypted database backups in production.

## Slide 13: OWASP and NIST Mapping
- OWASP A01 Broken Access Control: RBAC on dashboards and API.
- OWASP A03 Injection: parameterized database queries.
- OWASP A07 Identification and Authentication Failures: password hashing and login throttling.
- OWASP A09 Security Logging and Monitoring Failures: audit_events table and admin dashboard.
- NIST CSF: Identify risks, Protect with controls, Detect through logs, Respond through investigation.

## Slide 14: AI/ML in Cybersecurity
- AI can support intrusion detection by learning normal login and request behavior.
- ML can detect unusual donation patterns, repeated failed logins, and suspicious IP behavior.
- AI can help prioritize alerts for the admin/security team.
- AI is only supportive; secure coding, access control, patching, and monitoring remain mandatory.

## Slide 15: Cloud Security Architecture
- DNS/CDN/WAF receives public traffic.
- HTTPS load balancer forwards traffic to private app server.
- Private database is isolated from the internet.
- IAM roles enforce least privilege.
- KMS encrypts data and backups.
- Cloud monitoring/SIEM collects logs and alerts.
- Admin access requires MFA.

## Slide 16: Demonstration Flow
- Open home page and explain final review scope.
- Login as donor and submit valid donation.
- Show invalid payload rejection.
- Attempt admin dashboard using donor account and show blocked access.
- Login as admin and show donations, audit events, and failed login metrics.
- Open hardening and cloud/AI pages.

## Slide 17: Limitations and Future Scope
- Current app is a local educational simulation.
- Production should use HTTPS, reverse proxy, managed database, secret manager, and MFA.
- Add automated ZAP scan report.
- Add real SIEM integration.
- Add email alerts for repeated failed logins.
- Add payment gateway sandbox with PCI-DSS considerations.

## Slide 18: Conclusion
- The project demonstrates secure design, implementation, validation, and final hardening.
- Review 3 requirements are covered through integration, security improvements, OWASP/NIST mapping, AI/ML discussion, and cloud architecture.
- The demo is suitable for viva discussion on threats, controls, testing, and deployment security.

