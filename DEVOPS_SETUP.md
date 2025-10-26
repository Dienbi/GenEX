# GenEX DevOps Pipeline - Setup Guide

## 🚀 Quick Start

### Step 1: Pull Docker Images (Run in PowerShell/WSL)

```powershell
# Pull Jenkins
docker pull jenkins/jenkins:lts

# Pull SonarQube
docker pull sonarqube:lts-community

# Pull Python
docker pull python:3.9-slim
```

### Step 2: Start All Services

```powershell
# Navigate to project directory
cd D:\OneDrive\Bureau\GenEX

# Start Docker Compose
docker-compose up -d
```

### Step 3: Access Services

Wait 30-60 seconds for services to start, then access:

#### Jenkins: http://localhost:8080
- Get initial password:
  ```powershell
  docker exec genex_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  ```
- Install suggested plugins
- Create admin user

#### SonarQube: http://localhost:9000
- Default credentials: `admin` / `admin`
- Change password on first login
- Create a token for Jenkins integration

#### GenEX App: http://localhost:8000

---

## 📋 Pipeline Configuration

### Configure Jenkins

1. **Install Required Plugins:**
   - Go to: Manage Jenkins → Manage Plugins
   - Install:
     - SonarQube Scanner
     - Docker Pipeline
     - Pipeline
     - Git

2. **Add SonarQube Server:**
   - Go to: Manage Jenkins → Configure System
   - Find "SonarQube servers"
   - Add SonarQube:
     - Name: `SonarQube`
     - Server URL: `http://sonarqube:9000`
     - Server authentication token: (generate in SonarQube)

3. **Add SonarQube Scanner Tool:**
   - Go to: Manage Jenkins → Global Tool Configuration
   - Find "SonarQube Scanner"
   - Add SonarQube Scanner
     - Name: `SonarQubeScanner`
     - Install automatically: ✓

4. **Create Pipeline Job:**
   - New Item → Pipeline
   - Name: `GenEX-Pipeline`
   - Pipeline definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `https://github.com/Dienbi/GenEX.git`
   - Branch: `*/master`
   - Script Path: `Jenkinsfile`

### Configure SonarQube

1. **Generate Token:**
   - Login to SonarQube
   - My Account → Security → Generate Token
   - Copy token for Jenkins

2. **Create Project:**
   - Projects → Create Project
   - Project key: `genex`
   - Display name: `GenEX`
   - Setup: Manually

---

## 🐳 Docker Commands Reference

```powershell
# View running containers
docker-compose ps

# View logs
docker-compose logs -f [service_name]
# Example: docker-compose logs -f jenkins

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

---

## 🔧 Troubleshooting

### Jenkins won't start
```powershell
docker logs genex_jenkins
docker-compose restart jenkins
```

### SonarQube won't start
```powershell
# SonarQube needs more memory
wsl -d docker-desktop sysctl -w vm.max_map_count=262144
```

### Port conflicts
```powershell
# Check what's using a port
netstat -ano | findstr :8080
# Kill the process or change port in docker-compose.yml
```

### Reset everything
```powershell
docker-compose down -v
docker-compose up -d
```

---

## 📊 Pipeline Stages Explained

1. **Checkout** - Pull code from Git
2. **Environment Setup** - Install Python dependencies
3. **Linting** - Check code style with flake8
4. **Unit Tests** - Run Django tests
5. **Code Coverage** - Generate coverage reports
6. **SonarQube Analysis** - Code quality analysis
7. **Quality Gate** - Check if code passes quality standards
8. **Security Check** - Scan for vulnerabilities
9. **Build Docker Image** - Create container image
10. **Database Migrations** - Update database schema
11. **Collect Static Files** - Gather static assets
12. **Deploy** - Start the application
13. **Health Check** - Verify app is running

---

## 🎯 Running the Pipeline

1. Open Jenkins at http://localhost:8080
2. Click on `GenEX-Pipeline`
3. Click "Build Now"
4. Watch the pipeline execute
5. Check SonarQube for code quality reports

---

## 📈 Monitoring

- **Jenkins Build History**: http://localhost:8080/job/GenEX-Pipeline/
- **SonarQube Dashboard**: http://localhost:9000/dashboard?id=genex
- **Application**: http://localhost:8000

---

## 🛠️ Development Workflow

1. Make code changes
2. Commit and push to GitHub
3. Jenkins automatically triggers pipeline
4. Pipeline runs all tests and checks
5. If successful, deploys to Docker container
6. Check SonarQube for code quality metrics

---

## 🔒 Security Best Practices

1. Change default passwords immediately
2. Use environment variables for secrets
3. Never commit sensitive data
4. Review SonarQube security hotspots
5. Keep Docker images updated

---

## 📝 Notes

- First build may take 5-10 minutes
- SonarQube needs 2GB RAM minimum
- Jenkins needs Docker socket access
- Keep Docker Desktop running

---

For issues, check:
- Docker logs: `docker-compose logs`
- Jenkins console output
- SonarQube logs in the UI
