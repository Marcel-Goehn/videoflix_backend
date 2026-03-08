# VideoFlix Backend

A REST API backend for a Netflix-like video streaming platform, built with **Django REST Framework**. It serves HLS video streams and uses **JWT authentication** stored in HTTP-only cookies for secure, stateless sessions.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Django 6.0.2 + DRF 3.16.1 | Web framework & REST API |
| PostgreSQL | Relational database |
| Redis | Caching & job queue broker |
| Django RQ | Background task processing |
| Simple JWT | JWT auth via HTTP-only cookies |
| FFmpeg | Video transcoding & thumbnail generation |
| Docker / Docker Compose | Containerized deployment |
| Gunicorn | WSGI production server |
| WhiteNoise | Static file serving |

---

## Features

- Email-based user registration with account activation link
- JWT authentication stored in HTTP-only cookies
- Token refresh & logout with token blacklisting
- Password reset via email
- Video upload via the Django admin dashboard
- FFmpeg transcoding to HLS format (360p, 480p, 720p, 1080p)
- Automatic thumbnail generation on upload
- Non-blocking background video processing via Django RQ
- RESTful API for listing videos and streaming HLS content
- Automatic cleanup of HLS files when a video is deleted

---

## Prerequisites

- **Docker** & **Docker Compose** (recommended)

For local development without Docker:
- Python 3.12+
- PostgreSQL
- Redis
- FFmpeg (must be available on your `PATH`)

---

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <REPOSITORY_URL>
   cd videoflix-backend
   ```

2. **Configure environment variables**
   ```bash
   cp .env.template .env
   ```
   Open `.env` and fill in all required values (see [Environment Variables](#environment-variables) below).

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: `http://localhost:8000/api/`
   - Admin dashboard: `http://localhost:8000/admin/`

---

## Environment Variables

Copy `.env.template` to `.env` and set the following values:

### Django / App

| Variable | Description |
|---|---|
| `DJANGO_SUPERUSER_USERNAME` | Username for the auto-created Django superuser |
| `DJANGO_SUPERUSER_PASSWORD` | Password for the auto-created Django superuser |
| `DJANGO_SUPERUSER_EMAIL` | Email for the auto-created Django superuser |
| `SECRET_KEY` | Django secret key — use a long, random string in production |
| `DEBUG` | Set to `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames (e.g. `localhost,127.0.0.1`) |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated list of trusted origins for CSRF (e.g. `http://localhost:5500`) |

### Database (PostgreSQL)

| Variable | Description |
|---|---|
| `DB_NAME` | Name of the PostgreSQL database |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | Database host — use `db` when running with Docker Compose |
| `DB_PORT` | Database port (default: `5432`) |

### Redis

| Variable | Description |
|---|---|
| `REDIS_HOST` | Redis host — use `redis` when running with Docker Compose |
| `REDIS_LOCATION` | Full Redis URL used by the cache backend (e.g. `redis://redis:6379/1`) |
| `REDIS_PORT` | Redis port (default: `6379`) |
| `REDIS_DB` | Redis database index for the job queue (default: `0`) |

### Email (SMTP)

| Variable | Description |
|---|---|
| `EMAIL_HOST` | SMTP server hostname (e.g. `smtp.gmail.com`) |
| `EMAIL_PORT` | SMTP port (typically `587` for TLS) |
| `EMAIL_HOST_USER` | SMTP username / email address |
| `EMAIL_HOST_PASSWORD` | SMTP password or app-specific password |
| `EMAIL_USE_TLS` | Enable STARTTLS — set to `True` for port 587 |
| `EMAIL_USE_SSL` | Enable SSL — set to `True` for port 465 (mutually exclusive with TLS) |
| `DEFAULT_FROM_EMAIL` | The "From" address used in outgoing emails |

---

## Related Frontend

[VideoFlix Frontend](<LINK>)

---

## Author

[<NAME>](<GITHUB_LINK>)

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Feedback

For questions or feedback, reach out at: `<EMAIL_ADDRESS>`
