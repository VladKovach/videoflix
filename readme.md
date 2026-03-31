# Videoflix Backend

A Django REST Framework backend for Video-on-Demand streaming with email-based authentication, JWT cookie auth, PostgreSQL, Redis, and HLS playback endpoints.

## ✅ What this project provides

- Custom email-based auth with registration, account activation, login, logout, refresh token, password reset
- JWT auth stored in cookies: `access_token` and `refresh_token`
- Video listing API and HLS streaming endpoints
- PostgreSQL database and Redis cache/queue support
- Background video transcoding using `django-rq` + `ffmpeg`
- Admin panel support for managing users and videos

## 📦 Tech stack

- Python 3.8+
- Django 6.0
- Django REST Framework
- djangorestframework-simplejwt
- django-rq
- PostgreSQL
- Redis
- Docker / Docker Compose
- FFmpeg (installed inside the Docker image for video transcoding)

## 🔧 Docker setup

This project is designed to run with Docker and Docker Compose. A local Python virtual environment is not required.

### Prerequisites

- Docker Engine / Docker Desktop installed
- Docker Compose available as `docker compose`

### Setup

1. Copy the environment template:

```powershell
copy .env.template .env
```

2. Edit `.env` with your configuration.
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - `DB_HOST=db`
   - `DB_PORT=5432`
   - `REDIS_HOST=redis`
   - `REDIS_LOCATION=redis://redis:6379/1`
   - Email settings for account activation and password reset delivery

3. Build and start all services:

```powershell
docker compose up --build -d
```

4. Apply database migrations inside the backend container:

```powershell
docker compose exec web python manage.py migrate
```

5. Create a superuser inside the backend container:

```powershell
docker compose exec web python manage.py createsuperuser
```

6. Visit the app at `http://127.0.0.1:8000/`.

### Notes

- The Docker image installs `ffmpeg` and can run the transcode worker.
- The backend container is named `videoflix_backend` in `docker-compose.yml`.
- If you need to run commands manually in the web container, use:

```powershell
docker compose exec web sh
```

## 🧩 Environment variables

The project reads variables from `.env`. Important settings include:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `REDIS_HOST`, `REDIS_LOCATION`, `REDIS_PORT`, `REDIS_DB`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL`

## 🌐 API Endpoints

### Auth

- `POST /api/register/`
  - body: `email`, `password`, `confirmed_password`
  - sends account activation email

- `POST /api/login/`
  - body: `email`, `password`
  - returns user info and sets `access_token` and `refresh_token` cookies

- `POST /api/logout/`
  - clears auth cookies and blacklists refresh token

- `POST /api/token/refresh/`
  - refreshes `access_token` using the cookie refresh token

- `GET /api/activate/<uidb64>/<token>/`
  - activates the user account

- `POST /api/password_reset/`
  - sends password reset email

- `POST /api/password_confirm/<uidb64>/<token>/`
  - confirm and set the new password

### Video

- `GET /api/video/`
  - returns all videos with metadata

- `GET /api/video/<movie_id>/<resolution>/index.m3u8`
  - returns HLS playlist for a video resolution

- `GET /api/video/<movie_id>/<resolution>/<segment>/`
  - returns HLS segment file

## 🗃️ Models and features

- `auth_app.User`
  - custom user model using email as login field

- `video_app.Video`
  - stores title, description, thumbnail, category, uploaded video file, status
  - `status` values: `pending`, `processing`, `done`, `failed`

- Background video transcoding
  - `video_app.tasks.transcode_video` uses `ffmpeg` to build HLS segments and playlists
  - `django-rq` is configured in `core.settings`

## 🧪 Admin

- Visit `http://127.0.0.1:8000/admin/`
- Login with the superuser created via `createsuperuser`

## 🚀 Notes

- In development, email is sent via console backend by default.
- `access_token` / `refresh_token` cookies are configured for JWT authentication.
- `STATIC_ROOT` is `static/` and `MEDIA_ROOT` is `media/`.
- If you run with Docker Compose, the backend is exposed on port `8000`.

## 📌 Helpful commands

```powershell
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```
