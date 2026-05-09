# Hosting ImpactOps on a Subdomain

Target example: `portal.vishalkesharwani.in`

## Option A: Render / Railway / Similar Python Host

1. Push this repository to GitHub.
2. Create a new Web Service from the GitHub repo.
3. Use these settings:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:application --bind 0.0.0.0:$PORT`
4. Add environment variable:
   - `NGO_PORTAL_SECRET`: a long random string
5. Deploy the service.
6. Copy the generated service domain.
7. In your DNS manager for `vishalkesharwani.in`, create:
   - Type: `CNAME`
   - Name: `portal`
   - Value: the hosting provider domain
8. Enable HTTPS from the hosting provider dashboard.

## Option B: VPS With Nginx

1. Clone the repository on the server:
   ```bash
   git clone https://github.com/vishal-kesharwani/ngo-donation-portal.git
   cd ngo-donation-portal
   ```
2. Create virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run Gunicorn:
   ```bash
   NGO_PORTAL_SECRET="replace-with-long-secret" gunicorn wsgi:application --bind 127.0.0.1:8000
   ```
4. Configure Nginx:
   ```nginx
   server {
       server_name portal.vishalkesharwani.in;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
5. Point DNS `A` record:
   - Type: `A`
   - Name: `portal`
   - Value: your VPS public IP
6. Enable HTTPS:
   ```bash
   sudo certbot --nginx -d portal.vishalkesharwani.in
   ```

## Production Notes

- Keep `NGO_PORTAL_SECRET` private.
- Do not commit the SQLite database from `data/`.
- Put the app behind HTTPS.
- Use regular backups if real data is entered.
- For real payments, integrate only a trusted payment gateway and follow PCI-DSS guidance.

