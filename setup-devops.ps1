# GenEX DevOps Pipeline Setup Script for Windows
# Run this script in PowerShell to set up the complete CI/CD pipeline

Write-Host "🚀 GenEX DevOps Pipeline Setup Starting..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Step 1: Check WSL installation
Write-Host "📋 Step 1: Checking WSL installation..." -ForegroundColor Cyan
wsl --list --verbose
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ WSL not found! Please install WSL first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ WSL is installed" -ForegroundColor Green
Write-Host ""

# Step 2: Check Docker installation  
Write-Host "📋 Step 2: Checking Docker installation..." -ForegroundColor Cyan
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker not found! Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is installed" -ForegroundColor Green
Write-Host ""

# Step 3: Pull required Docker images
Write-Host "📋 Step 3: Pulling Docker images..." -ForegroundColor Cyan
Write-Host "⏳ Pulling Jenkins..." -ForegroundColor Yellow
docker pull jenkins/jenkins:lts

Write-Host "⏳ Pulling SonarQube..." -ForegroundColor Yellow
docker pull sonarqube:lts-community

Write-Host "⏳ Pulling Python..." -ForegroundColor Yellow
docker pull python:3.9-slim

Write-Host "✅ All Docker images pulled successfully" -ForegroundColor Green
Write-Host ""

# Step 4: Create Docker network
Write-Host "📋 Step 4: Creating Docker network..." -ForegroundColor Cyan
docker network create genex_network 2>$null
Write-Host "✅ Docker network ready" -ForegroundColor Green
Write-Host ""

# Step 5: Start Docker Compose services
Write-Host "📋 Step 5: Starting Docker Compose services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host ""

# Step 6: Display service information
Write-Host "📋 Step 6: Service Information" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Jenkins: http://localhost:8080" -ForegroundColor Yellow
Write-Host "   Username: admin" -ForegroundColor Gray
Write-Host "   Get initial password with: docker exec genex_jenkins cat /var/jenkins_home/secrets/initialAdminPassword" -ForegroundColor Gray
Write-Host ""
Write-Host "🔬 SonarQube: http://localhost:9000" -ForegroundColor Yellow
Write-Host "   Default Username: admin" -ForegroundColor Gray
Write-Host "   Default Password: admin" -ForegroundColor Gray
Write-Host ""
Write-Host "🌍 GenEX Application: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""

# Step 7: Get Jenkins initial password
Write-Host "📋 Step 7: Getting Jenkins initial password..." -ForegroundColor Cyan
Start-Sleep -Seconds 10
try {
    $jenkinsPassword = docker exec genex_jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>$null
    if ($jenkinsPassword) {
        Write-Host "🔑 Jenkins Initial Admin Password: $jenkinsPassword" -ForegroundColor Green
        Write-Host "   Please save this password!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Could not retrieve Jenkins password yet. Try: docker exec genex_jenkins cat /var/jenkins_home/secrets/initialAdminPassword" -ForegroundColor Yellow
}
Write-Host ""

# Step 8: Display next steps
Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open Jenkins at http://localhost:8080" -ForegroundColor White
Write-Host "2. Use the admin password shown above to unlock Jenkins" -ForegroundColor White
Write-Host "3. Install suggested plugins" -ForegroundColor White
Write-Host "4. Create your first admin user" -ForegroundColor White
Write-Host "5. Open SonarQube at http://localhost:9000 (admin/admin)" -ForegroundColor White
Write-Host "6. Change SonarQube admin password" -ForegroundColor White
Write-Host "7. In Jenkins, create a new Pipeline job" -ForegroundColor White
Write-Host "8. Point it to your Jenkinsfile in the repository" -ForegroundColor White
Write-Host ""
Write-Host "📚 Useful Commands:" -ForegroundColor Cyan
Write-Host "   View running containers: docker-compose ps" -ForegroundColor Gray
Write-Host "   View logs: docker-compose logs -f [service_name]" -ForegroundColor Gray
Write-Host "   Stop all services: docker-compose down" -ForegroundColor Gray
Write-Host "   Restart services: docker-compose restart" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Happy DevOps!" -ForegroundColor Green
