# ImpactOps Donor Management Platform

Structured Python implementation of a secure donor management platform for hosting under a subdomain such as `ngoportal.vishalkesharwani.in`.

## Run

```powershell
python .\run.py
```

Open:

- http://127.0.0.1:8000

## Demo Accounts

- Admin: `admin@ngo.local` / `Admin@1234`
- Donor: `donor@ngo.local` / `Donor@1234`

## Project Structure

```text
ngo_portal/
  config.py              app paths, session and throttling settings
  database.py            SQLite schema, seed data, user queries
  security.py            password hashing, signed sessions, security headers
  services.py            audit logging, login throttling, dashboard metrics
  validators.py          login and donation validation
  views.py               HTML view rendering
  web.py                 WSGI routes and request handling
  static/styles.css      UI styling
docs/
  review3_ppt_contents.md
run.py                   main server entrypoint
ngo_portal_review3.py    compatibility entrypoint
data/                    SQLite database folder
```

## Security Controls

- Authentication and RBAC
- CSRF protection
- Input validation
- Parameterized queries
- Audit logging
- Brute-force login throttling
- Security response headers
- Final review documentation in `docs/`

## Hosting

Use `wsgi.py` with Gunicorn for production-style hosting:

```bash
gunicorn wsgi:application --bind 0.0.0.0:$PORT
```

Subdomain deployment steps are in `HOSTING.md`.
