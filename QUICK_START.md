# 🚀 GenEX DevOps Pipeline - QUICK START COMMANDS

## ✅ Files Created:
1. ✅ Dockerfile - Containerizes the Django application
2. ✅ docker-compose.yml - Orchestrates all services (Jenkins, SonarQube, App)
3. ✅ Jenkinsfile - Complete CI/CD pipeline with 13 stages
4. ✅ sonar-project.properties - SonarQube configuration
5. ✅ .dockerignore - Excludes unnecessary files from Docker build
6. ✅ setup-devops.ps1 - Automated setup script
7. ✅ DEVOPS_SETUP.md - Complete setup guide

---

## 🎯 RUN THESE COMMANDS NOW:

### 1. Pull Docker Images (Required)
```powershell
# Pull Jenkins (already started in background)
docker pull jenkins/jenkins:lts

# Pull SonarQube  
docker pull sonarqube:lts-community

# Pull Python base image
docker pull python:3.9-slim
```

### 2. Start All Services
```powershell
docker-compose up -d
```

### 3. Wait 60 seconds, then access:

**Jenkins:** http://localhost:8080
- Get password:
  ```powershell
  docker exec genex_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  ```

**SonarQube:** http://localhost:9000
- Login: `admin` / `admin`

**Your App:** http://localhost:8000

---

## 📋 Pipeline Stages (13 Total):

```
1. Checkout Code from Git
2. Setup Python Environment
3. Run Linting (flake8)
4. Run Unit Tests
5. Generate Code Coverage
6. SonarQube Code Analysis
7. Quality Gate Check
8. Security Scan (safety, bandit)
9. Build Docker Image
10. Run Database Migrations
11. Collect Static Files
12. Deploy Application
13. Health Check
```

---

## ⚡ Alternative: Use Auto-Setup Script

```powershell
# Run the automated setup
.\setup-devops.ps1
```

This will:
- Check WSL & Docker
- Pull all images
- Start all services
- Display Jenkins password
- Show next steps

---

## 🔧 After Services Start:

### Configure Jenkins (5 minutes):
1. Open http://localhost:8080
2. Enter initial admin password
3. Install suggested plugins
4. Create admin user
5. Add SonarQube plugin
6. Configure SonarQube server
7. Create Pipeline job pointing to your Jenkinsfile

### Configure SonarQube (2 minutes):
1. Open http://localhost:9000
2. Login with admin/admin
3. Change password
4. Generate authentication token
5. Add token to Jenkins

---

## 📊 Useful Commands:

```powershell
# View all running containers
docker-compose ps

# View logs
docker-compose logs -f jenkins
docker-compose logs -f sonarqube
docker-compose logs -f web

# Stop all
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build
```

---

## 🎉 What You Get:

✅ Automated testing on every commit
✅ Code quality analysis with SonarQube
✅ Security vulnerability scanning
✅ Docker containerization
✅ Automated deployments
✅ Build history and logs
✅ Email notifications (configured in Jenkinsfile)

---

## 🐛 Common Issues:

**Port 8080 busy?**
```powershell
# Check what's using it
netstat -ano | findstr :8080
# Or change port in docker-compose.yml
```

**SonarQube won't start?**
```powershell
wsl -d docker-desktop sysctl -w vm.max_map_count=262144
```

**Need to reset?**
```powershell
docker-compose down -v
docker-compose up -d
```

---

## 📚 Next Steps:

1. ✅ Run: `docker pull jenkins/jenkins:lts`
2. ✅ Run: `docker pull sonarqube:lts-community`
3. ✅ Run: `docker-compose up -d`
4. ⏳ Wait 60 seconds
5. 🔑 Get Jenkins password
6. 🌐 Configure services
7. 🚀 Run your first pipeline build!

---

**Ready to start? Run these three commands:**

```powershell
docker pull jenkins/jenkins:lts && docker pull sonarqube:lts-community
docker-compose up -d
docker exec genex_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Good luck! 🎉
