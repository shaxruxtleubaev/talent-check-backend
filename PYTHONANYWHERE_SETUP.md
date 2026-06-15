# PythonAnywhere Deployment Guide

## Step 1: Push to GitHub

```bash
cd /Users/shaxruxxantleubaev/Documents/coding/gulnur_proekt/backend
git add -A
git commit -m "Clean backend for deployment"
git push origin main
```

## Step 2: Create PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up (free account works fine)
3. Go to Dashboard

## Step 3: Set Up Web App on PythonAnywhere

1. Click **Web** tab → **Add a new web app**
2. Choose "Manual configuration"
3. Select Python 3.10 or 3.11
4. You'll get a WSGI file path like `/var/www/yourusername_pythonanywhere_com_wsgi.py`

## Step 4: Clone Your Project

Open **Bash console** on PythonAnywhere:

```bash
cd /home/yourusername
git clone https://github.com/yourusername/gulnur_proekt.git
cd gulnur_proekt/backend
```

## Step 5: Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 6: Create Database

```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin account
python manage.py collectstatic --noinput
```

## Step 7: Configure WSGI File

In **Web** tab, find and edit your WSGI file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):

```python
# +++++++++++ DJANGO +++++++++++
import os
import sys

path = '/home/yourusername/gulnur_proekt/backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'src.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Step 8: Set Up Virtual Environment in Web App

In **Web** tab:
- Find "Virtualenv" section
- Enter path: `/home/yourusername/gulnur_proekt/backend/venv`

## Step 9: Configure Static Files

In **Web** tab, add static file mapping:
- URL: `/static/`
- Directory: `/home/yourusername/gulnur_proekt/backend/staticfiles`

## Step 10: Reload Web App

Click **Reload** button in **Web** tab.

Your app should now be live at `yourusername.pythonanywhere.com`!

## Step 11: Access Admin Panel

Go to `yourusername.pythonanywhere.com/admin/` and login with your superuser credentials.

## Troubleshooting

**If you get 500 error:**
- Check error log in Web tab
- Run `python manage.py check` in bash console
- Verify WSGI file path is correct

**If static files don't load:**
- Run `python manage.py collectstatic --clear --noinput` again
- Check static files mapping path in Web tab

**If database is missing:**
```bash
cd /home/yourusername/gulnur_proekt/backend
python manage.py migrate
```

## Future Updates

To update your app with new code:

```bash
cd /home/yourusername/gulnur_proekt/backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** in Web tab.
