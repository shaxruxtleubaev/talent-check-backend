# TalentCheck Backend

Django REST API for the TalentCheck pedagogical monitoring platform.

## Prerequisites

- Python 3.10+
- pip

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/gulnur_proekt.git
cd gulnur_proekt/backend
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env file
```bash
cp .env.example .env
```
Edit `.env` and set your configuration values.

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Collect static files
```bash
python manage.py collectstatic --noinput
```

### 8. Run development server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Deployment to PythonAnywhere

### 1. Upload to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. On PythonAnywhere

1. Create a new account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to Web tab and add a new web app
3. Choose Python 3.10 and Django
4. In Bash console, clone your repo:
```bash
cd /home/yourusername
git clone https://github.com/yourusername/gulnur_proekt.git
```

5. Create virtual environment:
```bash
cd gulnur_proekt/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

6. Create `.env` file with production settings
7. Run migrations:
```bash
python manage.py migrate
```

8. Create superuser:
```bash
python manage.py createsuperuser
```

9. Collect static files:
```bash
python manage.py collectstatic --noinput
```

10. Configure WSGI file in PythonAnywhere Web tab
11. Set up environment variables in PythonAnywhere settings
12. Reload the web app

## Environment Variables

See `.env.example` for all available options. Key variables:

- `DEBUG` - Set to `False` in production
- `SECRET_KEY` - Generate a strong secret key
- `ALLOWED_HOSTS` - Add your domain
- `CORS_ALLOWED_ORIGINS` - Add your frontend URL

## API Endpoints

- `POST /api/auth/login/` - User login
- `GET /api/user/profile/` - Get user profile
- `GET /api/tests/` - List all tests
- `GET /api/tests/{id}/` - Get test details
- `POST /api/tests/{id}/submit/` - Submit test
- `GET /api/user/results/` - Get user results

## Admin Panel

Access at `/admin/` with your superuser credentials.

## Security Notes

- Never commit `.env` file with real credentials
- Keep `SECRET_KEY` secret in production
- Set `DEBUG=False` in production
- Use environment variables for all sensitive data
- Set up HTTPS in production

## Troubleshooting

### Database issues
```bash
python manage.py migrate --run-syncdb
```

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Permission errors
Make sure your PythonAnywhere username matches in settings and file permissions are correct.

## Support

For issues or questions, contact the development team.
