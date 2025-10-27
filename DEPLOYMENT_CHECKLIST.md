# ✅ Render Deployment Checklist

## 📦 What Was Done

### Backups Created ✅

- [x] `db.sqlite3.backup` - Full database backup
- [x] `GenEX/settings.py.backup` - Original settings
- [x] `requirements.txt.backup` - Original requirements

### Files Created ✅

- [x] `build.sh` - Render build script
- [x] `render.yaml` - Service configuration
- [x] `RENDER_DEPLOYMENT.md` - Full deployment guide
- [x] `DEPLOYMENT_SUMMARY.md` - Changes summary
- [x] `.env.example` - Environment variables template

### Files Modified ✅

- [x] `GenEX/settings.py` - PostgreSQL support + security
- [x] `requirements.txt` - Added production dependencies

### Dependencies Installed Locally ✅

- [x] `psycopg2-binary` - PostgreSQL adapter
- [x] `dj-database-url` - Parse DATABASE_URL
- [x] `gunicorn` - Production WSGI server
- [x] `whitenoise` - Static file serving

### Git ✅

- [x] All changes committed
- [x] Pushed to GitHub

---

## 🚀 Next Steps - Deploy to Render

### 1. Create Render Account

- [ ] Go to https://render.com
- [ ] Sign up with GitHub account
- [ ] Authorize Render to access Dienbi/GenEX repo

### 2. Create PostgreSQL Database

- [ ] Click "New +" → "PostgreSQL"
- [ ] Name: `genex-db`
- [ ] Database: `genex`
- [ ] User: `genex`
- [ ] Plan: **Free**
- [ ] Create Database
- [ ] **COPY** the Internal Database URL (starts with `postgresql://`)

### 3. Create Web Service

- [ ] Click "New +" → "Web Service"
- [ ] Connect repository: **Dienbi/GenEX**
- [ ] Name: `genex` (or your choice)
- [ ] Runtime: **Python 3**
- [ ] Build Command: `./build.sh`
- [ ] Start Command: `gunicorn GenEX.wsgi:application`
- [ ] Plan: **Free**

### 4. Add Environment Variables

Click "Environment" tab and add these:

- [ ] `PYTHON_VERSION` = `3.9.13`
- [ ] `SECRET_KEY` = (Click "Generate" button)
- [ ] `DEBUG` = `False`
- [ ] `DATABASE_URL` = (Paste Internal Database URL from step 2)
- [ ] `ALLOWED_HOSTS` = (Your domain, e.g., `genex.onrender.com`)
- [ ] `GROQ_API_KEY` = `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`
- [ ] `SITE_URL` = (Your URL, e.g., `https://genex.onrender.com`)

### 5. Deploy & Create Admin

- [ ] Click "Create Web Service"
- [ ] Wait 5-10 minutes for deployment
- [ ] Go to "Shell" tab
- [ ] Run: `python manage.py createsuperuser`
- [ ] Create admin credentials

### 6. Test Your Application

- [ ] Visit: `https://your-service.onrender.com`
- [ ] Login: `https://your-service.onrender.com/users/login/`
- [ ] Admin: `https://your-service.onrender.com/admin/`
- [ ] Backoffice: `https://your-service.onrender.com/users/backoffice/`

---

## 📚 Documentation

Read these files for detailed information:

1. **RENDER_DEPLOYMENT.md** - Complete step-by-step guide
2. **DEPLOYMENT_SUMMARY.md** - What changed and why
3. **.env.example** - Environment variables template

---

## ⚠️ Important Notes

### Local Development Still Works! ✅

```bash
# Your local setup is unchanged:
python manage.py runserver
# Uses SQLite, all your data is safe
```

### Databases Are Separate

- **Local**: SQLite with your test data
- **Production**: PostgreSQL (starts empty)
- They DON'T sync (this is normal!)

### Free Tier Limitations

- ⏰ Spins down after 15 min inactivity (first request slow)
- 💾 512 MB RAM
- 🔄 90-day database retention
- 🆓 Completely free!

---

## 🆘 Need Help?

### Troubleshooting

Check `RENDER_DEPLOYMENT.md` → "Troubleshooting" section

### Common Issues

1. **Build fails** → Check logs in Render dashboard
2. **Static files missing** → Verify `collectstatic` runs in build.sh
3. **Database error** → Check DATABASE_URL is set correctly
4. **500 error** → Set DEBUG=True temporarily to see details

### Rollback (if needed)

```bash
# Restore original files:
Copy-Item GenEX/settings.py.backup -Destination GenEX/settings.py
Copy-Item requirements.txt.backup -Destination requirements.txt
Copy-Item db.sqlite3.backup -Destination db.sqlite3
```

---

## 🎯 Success Criteria

✅ Website accessible at Render URL
✅ Can login and create users
✅ Backoffice works for admins
✅ Static files load correctly
✅ Database persists between deploys
✅ Migrations run automatically on deploy

---

**Good luck with your deployment! 🚀**

Need help? Check the documentation files or review the commit on GitHub.
