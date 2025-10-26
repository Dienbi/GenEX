# Render Deployment Guide for GenEX

## 📋 Prerequisites

✅ Database backup created: `db.sqlite3.backup`
✅ Settings backup created: `GenEX/settings.py.backup`
✅ Requirements backup created: `requirements.txt.backup`

## 🚀 Deployment Steps

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Add Render deployment configuration with PostgreSQL support"
git push origin master
```

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### 3. Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. **Name**: `genex-db`
3. **Database**: `genex`
4. **User**: `genex`
5. **Region**: Choose closest to you
6. **Plan**: **Free**
7. Click **"Create Database"**
8. **IMPORTANT**: Copy the **"Internal Database URL"** (starts with `postgresql://`)

### 4. Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: **Dienbi/GenEX**
3. Configure:
   - **Name**: `genex` (or your choice)
   - **Region**: Same as database
   - **Branch**: `master`
   - **Runtime**: **Python 3**
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn GenEX.wsgi:application`
   - **Plan**: **Free**

### 5. Add Environment Variables

Click **"Environment"** tab and add:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.9.13` |
| `SECRET_KEY` | Generate random (click "Generate") |
| `DEBUG` | `False` |
| `DATABASE_URL` | Paste the Internal Database URL from step 3 |
| `ALLOWED_HOSTS` | Your render domain (e.g., `genex.onrender.com`) |
| `GROQ_API_KEY` | `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` |
| `SITE_URL` | Your render URL (e.g., `https://genex.onrender.com`) |

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Run `build.sh` (install dependencies, collect static, migrate)
   - Start the application with Gunicorn
3. Wait 5-10 minutes for first deployment

### 7. Create Superuser (Admin Account)

After deployment succeeds:

1. Go to your web service dashboard
2. Click **"Shell"** tab (terminal icon)
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Enter admin credentials

### 8. Access Your Application

- **Website**: `https://your-service-name.onrender.com`
- **Admin**: `https://your-service-name.onrender.com/admin`
- **Backoffice**: `https://your-service-name.onrender.com/users/backoffice/`

## 🔧 Important Notes

### Free Plan Limitations

⚠️ **Free tier spins down after 15 minutes of inactivity**
- First request after inactivity takes ~30-60 seconds
- Database has 90-day retention limit
- 512 MB RAM, 0.1 CPU

### Database Backups

```bash
# On Render Shell, backup database to JSON
python manage.py dumpdata --exclude contenttypes --exclude auth.permission > backup.json

# Download using Render dashboard: Storage → Files
```

### Updating Your App

Every time you push to GitHub:
```bash
git add .
git commit -m "Your changes"
git push origin master
```

Render automatically:
1. Detects the push
2. Runs `build.sh`
3. Applies new migrations
4. Restarts the app

## 🐛 Troubleshooting

### Build Fails

**Check logs**: Render dashboard → "Logs" tab

Common issues:
- Missing dependencies → Update `requirements.txt`
- Migration errors → Check `build.sh` logs
- Static files → Ensure `collectstatic` runs

### Database Connection Error

- Verify `DATABASE_URL` environment variable
- Check database is running (not suspended)
- Ensure using **Internal** Database URL (not External)

### Static Files Not Loading

```python
# In settings.py, verify:
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Application Error 500

1. Set `DEBUG=True` temporarily to see error
2. Check logs in Render dashboard
3. Verify all environment variables are set

## 📊 Monitoring

- **Metrics**: Render dashboard → "Metrics" tab
- **Logs**: Real-time application logs
- **Events**: Deployment history

## 🔒 Security Checklist

✅ `DEBUG=False` in production
✅ `SECRET_KEY` is randomly generated
✅ `ALLOWED_HOSTS` configured
✅ Database password is secure
✅ HTTPS enabled (automatic on Render)
✅ Security headers configured

## 📝 Next Steps

1. Configure custom domain (optional)
2. Set up email service (SendGrid, Mailgun)
3. Configure media file storage (AWS S3, Cloudinary)
4. Enable monitoring and alerts
5. Set up backup strategy

## 🆘 Support

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [PostgreSQL on Render](https://render.com/docs/databases)

---

## 🎯 Quick Commands

```bash
# Local development (SQLite)
python manage.py runserver

# Check migrations
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser
```

Good luck with your deployment! 🚀
