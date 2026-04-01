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

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/VladKovach/videoflix.git
cd videoflix
```

### Step 2: Copy the environment template

```bash
cp .env.template .env
```

### Step 3: Update `.env`

Open `.env` and change these fields:

- `DB_NAME` (your preferred name for DB),
- `DB_USER` (your preferred DB user name),
- `DB_PASSWORD` (your preferred password for DB)

Generate a 16-character app password from your Google account security settings:

1. Go to `https://myaccount.google.com/security`
2. Enable 2-Step Verification if it is not already enabled
3. In "Search" tab, type "app passwords" and pick the first result
4. Create a new app password named as you want
5. In `.env` change these fields:

- `EMAIL_HOST_USER` (your email address)
- `EMAIL_HOST_PASSWORD` (your new app password)

⚠️ Tip: if you have a frontend for Videoflix, make sure your `index.html` runs on `5500` port; If not, you can change `5500` port in `.env` to the one on which your `index.html` runs.

### Step 4: Build and start with Docker Compose

```bash
docker compose up --build -d
```

### Step 5: Apply database migrations

```bash
docker compose exec web python manage.py migrate
```

⚠️ Tip: If you see the error `service "web" is not running`, open `backend.entrypoint.sh` and make sure your line endings are set to LF instead of CRLF (bottom right in your editor). Save the file and try again.

### Step 6: Access the application

Open `http://127.0.0.1:8000/` in your browser.

## 🧩 Environment variables

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
  - confirms and sets a new password

### Video

- `GET /api/video/`
  - returns all videos with metadata

- `GET /api/video/<movie_id>/<resolution>/index.m3u8`
  - returns HLS playlist for a video resolution

- `GET /api/video/<movie_id>/<resolution>/<segment>/`
  - returns HLS segment file

## 🧪 Admin

- Visit `http://127.0.0.1:8000/admin/`
- Login with the DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD from .env

## 🗃️ Background video transcoding

- Background video transcoding
  - Add a new video in the admin panel
  - A worker will transcode it in the background
  - Once the video status is set to "done", it will be available in 360p, 480p, 720p, and 1080p
